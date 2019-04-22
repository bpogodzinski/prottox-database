from natsort import natsorted

from django.http import JsonResponse
from prottox.models import FactorTaxonomy, SpeciesTaxonomy


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
    data = __processJSTreeTaxonomyQuerysetToJSON(queryset, 'factor')
    return JsonResponse(data, safe=False)


def targetTaxonomyAPI(request):
    queryset = SpeciesTaxonomy.objects.all()
    queryset = natsorted(queryset, lambda x: x.name)
    data = __processJSTreeTaxonomyQuerysetToJSON(queryset, 'taxonomy')
    return JsonResponse(data, safe=False)


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
        json_data.append(dict(id=node_id, parent=node_parent, text=node_text, entity=table))
    return json_data