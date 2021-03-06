from natsort import natsorted
import pandas as pd

from django.http import JsonResponse
from django.urls import reverse
from prottox.models import FactorTaxonomy, SpeciesTaxonomy, Toxin_research

PUBMED_LINK_TEMPLATE = "https://www.ncbi.nlm.nih.gov/pubmed/{ID}"
DATATABLE_VISIBLE_COLUMNS = ['Target species', 'Toxin', 'Toxin quantity', 'Toxicity measure', 'Observed toxicity', 'Interaction', 'Synergism factor (percentile)', 'Publication']
DATATABLE_DATA_COLUMNS = ['Toxin', 'Target species', 'Target developmental stage', 'Recognised resistance in target species', 'Bioassay duration (days)', 'Toxin quantity', 'Toxin administration method', 'Toxicity measure', 'Observed toxicity', 'Expected toxicity', '95% Fiducial limits', 'Interaction', 'Synergism factor', 'Synergism factor (percentile)', 'Interaction estimation model', 'Single toxin / Combination', 'Publication']
SYNERGISM_BADGE = '<span class="kt-badge kt-badge--success kt-badge--inline">{level} SYN</span>'
ANTAGONISM_BADGE = '<span class="kt-badge kt-badge--danger kt-badge--inline">{level} ANT</span>'
INDEPENDENT_BADGE = '<span class="kt-badge kt-badge--dark kt-badge--inline">Additive</span>'
BADGE_DICT = {'SYN': SYNERGISM_BADGE, 'ANT':ANTAGONISM_BADGE, 'IND':INDEPENDENT_BADGE}

def factorTaxonomyAPI(request):
    queryset = FactorTaxonomy.objects.all()

    if request.GET.get("parent"):
        queryset = __processFactorTaxonomyQuerysetParent(
            request.GET.get("parent")
        )
    if request.GET.get("parent_id"):
        queryset = __processFactorTaxonomyQuerysetParentID(
            request.GET.get("parent_id")
        )

    queryset = natsorted(queryset, lambda x: x.fullname)
    data = __processJSTreeTaxonomyQuerysetToJSON(queryset, "factor")
    return JsonResponse(data, safe=False)


def targetTaxonomyAPI(request):
    queryset = SpeciesTaxonomy.objects.all()
    queryset = natsorted(queryset, lambda x: x.name)
    data = __processJSTreeTaxonomyQuerysetToJSON(queryset, "taxonomy")
    return JsonResponse(data, safe=False)


def researchBrowserAPI(request):
    ids = request.GET.get('ids').strip().split(',')
    db = request.GET.get('db').strip()

    if db == "factor":
        queryset = Toxin_research.objects.filter(
            toxin__taxonomy__in=ids
        ).distinct()
    else:
        queryset = Toxin_research.objects.filter(
            target__target_organism_taxonomy__in=ids
        ).distinct()
    data = __processDatatableToxinResearchToJSON(queryset)
    return JsonResponse(data)


# ------------- BEGIN factor processing methods -----------------


def __processFactorTaxonomyQuerysetParent(param):
    """Process GET request parameters for parent by name

    Parent GET request parameters are splited by "," and filtered

    Example:
        ?parent=Cry,1,A -> [Cry,1,A] -> filter queryset by parent accordingly -> Cry1Aa, Cry1Ab, Cry1Ac ...

    Returns:
        fitered queryset
    """
    param = param.split(",") if isinstance(param, str) else param
    if len(param) == 1:
        parent = param.pop()
        return (
            FactorTaxonomy.objects.filter(parent__name__exact=parent)
            if parent != "none"
            else FactorTaxonomy.objects.filter(parent__isnull=True)
        )
    else:
        # Create **kwargs dictionary
        filters = dict()
        base_format = "{}parent__name__exact"
        for parent_level in range(len(param)):
            filters[base_format.format("parent__" * parent_level)] = param.pop()
        return FactorTaxonomy.objects.filter(**filters)


def __processFactorTaxonomyQuerysetParentID(param):
    """Process GET request parameters for parent by ID
    """
    return (
        FactorTaxonomy.objects.filter(parent__id=param)
        if param != "0"
        else FactorTaxonomy.objects.filter(parent__isnull=True)
    )


# ------------- END factor processing methods -----------------



# ------------- BEGIN JSON processing methods -----------------

def __processJSTreeTaxonomyQuerysetToJSON(queryset, table):
    """Changes queryset to JSON for jsTree to use
    """

    json_data = []
    for taxonomy in queryset:
        node_id = str(taxonomy.id)
        node_parent = (
            str(taxonomy.parent_id) if taxonomy.parent_id is not None else "#"
        )
        node_text = str(taxonomy)
        if 'Cry6' in node_text:
            alternative_name = node_text.replace('Cry6', 'App6')
            node_text = f"{node_text} ({alternative_name})"
        elif 'Cry55' in node_text:
            alternative_name = node_text.replace('Cry55', 'Xpp54')
            node_text = f"{node_text} ({alternative_name})"
        elif 'Sip1A' in node_text:
            alternative_name = node_text.replace('Sip1A', 'Mpp5A')
            node_text = f"{node_text} ({alternative_name})"
        json_data.append(
            dict(id=node_id, parent=node_parent, text=node_text, entity=table)
        )
    return json_data

def __processDatatableToxinResearchToJSON(queryset):
    json = dict(data=[], columns=[])
    for record in queryset:
        entry = {}
        entry['Toxin'] = __getDataTableFactors(record.toxin.all(), record.pk)
        entry['Target species'] = f'<i>{record.target.target_organism_taxonomy.name}</i>'
        entry['Target developmental stage'] = record.target.larvae_stage.stage
        entry['Recognised resistance in target species'] = record.target.factor_resistance
        entry['Bioassay duration (days)'] = 'N/A' if record.days_of_observation == 'nan' else record.days_of_observation
        entry['Toxin quantity'] = record.quantity.quantity if record.quantity else None
        entry['Toxin administration method'] = 'N/A' if record.toxin_distribution.distribution_choice == 'nan' else record.toxin_distribution.distribution_choice
        entry['Toxicity measure'] = record.results.bioassay_type.bioassay_type
        entry['Observed toxicity'] = __getDataTableBioassayResult(record.results) if record.results.bioassay_result else None
        entry['Expected toxicity'] = __getDataTableBioassayResult(record.results, expected=True) if record.results.expected else None
        entry['95% Fiducial limits'] = __getDataTableFiducialLimits(record.results)
        entry['Interaction'] = BADGE_DICT.get(record.results.interaction, record.results.interaction).format(**__getBadgeFormat(record.results.synergism_factor, record.results.interaction, record.results.percentile))
        entry['Synergism factor (percentile)'] = __getDataTableSynergismFactor(__roundOrEmptyString(record.results.synergism_factor, 2), record.results.percentile)
        entry['Interaction estimation model'] = record.results.estimation_method
        entry['Single toxin / Combination'] = record.label.split('(')[0]
        entry['Publication'] = __getDataTablePublication(record.publication)
        json['data'].append(entry)

    for name in json['data'][0].keys():
        entry = {}
        entry['title'] = name
        entry['data'] = name
        entry['visible'] = name in DATATABLE_VISIBLE_COLUMNS
        entry['name'] = name
        json['columns'].append(entry)

    return json

def __getBadgeFormat(SF, interaction, percentile):
    return_dict = {'level':''}
    if percentile:
        SF = float(SF.replace(',', '.'))
        if interaction == 'SYN':
            if 1 <= SF < 2:
                return_dict['level'] = 'Weak'
            elif 2 <= SF < 10:
                return_dict['level'] = 'Moderate'
            elif 10 <= SF:
                return_dict['level'] = 'Strong'
        elif interaction == 'ANT':
            if 0.5 <= SF < 1:
                return_dict['level'] = 'Weak'
            elif 0.1 <= SF < 0.5:
                return_dict['level'] = 'Moderate'
            elif 0 <= SF < 0.1:
                return_dict['level'] = 'Strong'

    return return_dict

def __getDataTableSynergismFactor(SF, percentile):
    string_percentile = ''
    if SF:
        if percentile:
            string_percentile = f'({percentile}ᵗʰ)'
        return f'{SF} {string_percentile}'
    else:
        return ''
# ------------- END JSON processing methods -----------------


# ------------- BEGIN DataTable processing methods -----------------

def __getDataTableFactors(activeFactors, pk):
    namelist = [factor.fullname for factor in activeFactors]
    for index, name in enumerate(namelist):
        if 'Cry6' in name:
            alternative_name = name.replace('Cry6', 'App6')
            namelist[index] = f"{name} ({alternative_name})"
        elif 'Cry55' in name:
            alternative_name = name.replace('Cry55', 'Xpp54')
            namelist[index] = f"{name} ({alternative_name})"
        elif 'Sip1A' in name:
            alternative_name = name.replace('Sip1A', 'Mpp5A')
            namelist[index] = f"{name} ({alternative_name})"

    return f"<a href={reverse('research_view', kwargs={'db_id':pk})}>{' + '.join(namelist)}<a/>"

def __getDataTableBioassayResult(results, expected=False):
    if expected:
        return f"{results.expected.replace(',','.')} {results.bioassay_unit}" if results.expected != "refer to source article" else "refer to source article"
    else:
        return f"{results.bioassay_result.replace(',','.')} {results.bioassay_unit}" if results.bioassay_result != "refer to source article" else "refer to source article"

def __getDataTablePublication(publication):
    allAuthors = ", ".join(sorted([author.fullname for author in publication.authors.all()]))

    if publication.pubmed_id:
        return f"<a href={PUBMED_LINK_TEMPLATE.format(ID=publication.pubmed_id)}>{publication.date.year} {allAuthors}</a>"
    elif publication.article_link:
        return f"<a href={publication.article_link}>{publication.date.year} {allAuthors}</a>"
    else:
        return f"{publication.date.year} {allAuthors}"

def __getDataTableFiducialLimits(results):
    return f"{results.LC95min} - {results.LC95max}"

# ------------- END DataTable processing methods -----------------

# ------------- BEGIN Custom funtions -----------------

def __roundOrEmptyString(number, ndigits=None):
    try:
        return round(float(number.replace(',','.')), ndigits)
    except ValueError:
        return ''

# ------------- END Custom funtions -----------------