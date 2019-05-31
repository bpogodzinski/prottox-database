from natsort import natsorted

from django.http import JsonResponse
from prottox.models import FactorTaxonomy, SpeciesTaxonomy, Toxin_research

PUBMED_LINK_TEMPLATE = "https://www.ncbi.nlm.nih.gov/pubmed/{ID}"
DATATABLE_VISIBLE_COLUMNS = ['Target species', 'Factor', 'Bioassay type', 'Bioassay result', 'Interaction', 'Publication']
    

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
        entry['Factor'] = __getDataTableFactors(record.toxin.all())
        entry['Target species'] = record.target.target_organism_taxonomy.name
        entry['Bioassay type'] = record.results.bioassay_type.bioassay_type
        entry['Bioassay result'] = __getDataTableBioassayResult(record.results) if record.results.bioassay_result else None
        entry['Interaction'] = record.results.interaction
        entry['Publication'] = __getDataTablePublication(record.publication)
        entry['Days of observation'] = record.days_of_observation
        entry['Toxin distribution'] = record.toxin_distribution.distribution_choice
        entry['Toxin quantity'] = record.quantity.quantity if record.quantity else None
        entry['Bioassay expected'] = __getDataTableBioassayResult(record.results, expected=True) if record.results.expected else None
        entry['Synergism factor'] = record.results.synergism_factor
        entry['Antagonism factor'] = record.results.antagonism_factor
        entry['Estimation method'] = record.results.estimation_method
        entry['Statistics'] = __getDataTableStatistics(record.results)
        entry['Target factor resistance'] = record.target.factor_resistance
        entry['Target larvae stage'] = record.target.larvae_stage.stage

        json['data'].append(entry)

    for name in json['data'][0].keys():
        entry = {}
        entry['title'] = name
        entry['data'] = name
        #entry['visible'] = name in DATATABLE_VISIBLE_COLUMNS

        json['columns'].append(entry)

    return json

# ------------- END JSON processing methods -----------------


# ------------- BEGIN DataTable processing methods -----------------

def __getDataTableFactors(activeFactors):
    return " + ".join(natsorted([factor.fullname for factor in activeFactors]))

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

def __getDataTableStatistics(result):
    statistics = ''
    if result.slopeLC:
        statistics += f"Slope LC: {result.slopeLC} "
    if result.slopeSE:
        statistics += f"Slope standard err: {result.slopeSE} "
    if result.chi_square:
        statistics += f"Chi-square: {result.chi_square}"

    return statistics
# ------------- END DataTable processing methods -----------------
