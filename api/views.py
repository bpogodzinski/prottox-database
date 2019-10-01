from natsort import natsorted

from django.http import JsonResponse
from django.urls import reverse
from prottox.models import FactorTaxonomy, SpeciesTaxonomy, Toxin_research

PUBMED_LINK_TEMPLATE = "https://www.ncbi.nlm.nih.gov/pubmed/{ID}"
DATATABLE_VISIBLE_COLUMNS = ['Select', 'Target species', 'Factor', 'Bioassay type', 'Bioassay result', 'Interaction', 'Publication']
DATATABLE_DATA_COLUMNS = ['Select', 'Factor', 'Target species', 'Target larvae stage', 'Target factor resistance', 'Days of observation', 'Toxin quantity', 'Toxin distribution', 'Bioassay type', 'Bioassay result observed', 'Bioassay result expected', '95% Fiducial limits', 'Interaction', 'Synergism factor', 'Estimation method', 'Publication']
SYNERGISM_BADGE = '<span class="kt-badge kt-badge--success kt-badge--inline">Synergism</span>'
ANTAGONISM_BADGE = '<span class="kt-badge kt-badge--danger kt-badge--inline">Antagonism</span>'
INDEPENDENT_BADGE = '<span class="kt-badge kt-badge--dark kt-badge--inline">Independent</span>'
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
        if param is not "0"
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
        json_data.append(
            dict(id=node_id, parent=node_parent, text=node_text, entity=table)
        )
    return json_data

def __processDatatableToxinResearchToJSON(queryset):
    json = dict(data=[], columns=[])
    for record in queryset:
        entry = {}
        entry['Select'] = ''
        entry['Factor'] = __getDataTableFactors(record.toxin.all(), record.pk)
        entry['Target species'] = record.target.target_organism_taxonomy.name
        entry['Target larvae stage'] = record.target.larvae_stage.stage
        entry['Target factor resistance'] = record.target.factor_resistance
        entry['Days of observation'] = record.days_of_observation
        entry['Toxin quantity'] = record.quantity.quantity if record.quantity else None
        entry['Toxin distribution'] = record.toxin_distribution.distribution_choice
        entry['Bioassay type'] = record.results.bioassay_type.bioassay_type
        entry['Bioassay result observed'] = __getDataTableBioassayResult(record.results) if record.results.bioassay_result else None
        entry['Bioassay result expected'] = __getDataTableBioassayResult(record.results, expected=True) if record.results.expected else None
        entry['95% Fiducial limits'] = __getDataTableFiducialLimits(record.results)
        entry['Interaction'] = BADGE_DICT.get(record.results.interaction, record.results.interaction)
        entry['Synergism factor'] = record.results.synergism_factor
        entry['Estimation method'] = record.results.estimation_method
        entry['Publication'] = __getDataTablePublication(record.publication)
        entry['DT_RowId'] = record.id
        json['data'].append(entry)

    for name in json['data'][0].keys():
        entry = {}
        entry['title'] = name
        entry['data'] = name
        entry['visible'] = name in DATATABLE_VISIBLE_COLUMNS
        entry['name'] = name
        json['columns'].append(entry)

    return json

# ------------- END JSON processing methods -----------------


# ------------- BEGIN DataTable processing methods -----------------

def __getDataTableFactors(activeFactors, pk):
    return f"<a href={reverse('research_view', kwargs={'db_id':pk})}>{' + '.join([factor.fullname for factor in activeFactors])}<a/>"

def __getDataTableBioassayResult(results, expected=False):
    if expected:
        return f"{results.expected} {results.bioassay_unit}" if results.expected != "reference" else "reference"
    else:
        return f"{results.bioassay_result} {results.bioassay_unit}" if results.bioassay_result != "reference" else "reference"

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
