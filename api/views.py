from natsort import natsorted

from django.http import JsonResponse
from prottox.models import FactorTaxonomy, SpeciesTaxonomy, Toxin_research


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
        entry['Target species'] = record.target.target_organism_taxonomy.name
        entry['Factor'] = __getDataTableFactors(record.toxin)
        entry['Bioassay type'] = record.results.bioassay_type.bioassay_type
        entry['Bioassay result'] = __getDataTableBioassayResult(record.results)
        entry['Interaction'] = record.results.interaction

        json['data'].append(entry)

    for name in json['data'][0].keys():
        entry = {}
        entry['title'] = name
        entry['data'] = name

        json['columns'].append(entry)

    return json

# ------------- END JSON processing methods -----------------


# ------------- BEGIN DataTable processing methods -----------------

def __getDataTableFactors(activeFactors):
    return " + ".join(natsorted([factor.fullname for factor in activeFactors.all()]))

def __getDataTableBioassayResult(results):
    return f"{results.bioassay_result} {results.bioassay_unit}"

# ------------- END DataTable processing methods -----------------
