import json
from natsort import natsorted

from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from prottox.models import *


def taxonomyAPI(request):
    queryset = Taxonomy.objects.all()

    if request.GET.get('parent'):
        queryset = __processTaxonomyQuerysetParent(request.GET.get('parent'))
    if request.GET.get('parent_id'):
        queryset = __processTaxonomyQuerysetParentID(request.GET.get('parent_id'))
   
    data = __processTaxonomyQuerysetToJSON(queryset)
    return JsonResponse(data, safe=False)

def activeFactorAPI(request):
    pass

    

#------------- Processing methods -----------------

def __processTaxonomyQuerysetParent(param):
    """Process GET request parameters for parent by name

    Parent GET request parameters are splited by "," and filtered

    Example:
        ?parent=Cry,1,A -> [Cry,1,A] -> filter queryset by parent accordingly -> Cry1Aa, Cry1Ab, Cry1Ac ...

    Returns:
        fitered queryset
    """
    param = param.split(',') if type(param) == str else param
    if len(param) == 1:
        parent = param.pop()
        return Taxonomy.objects.filter(parent__name__exact=parent) if parent != 'none' else Taxonomy.objects.filter(parent__isnull=True)
    else: 
        #Create **kwargs dictionary
        filters = dict()
        baseFormat = '{}parent__name__exact'
        for parentLevel in range(len(param)):
            filters[baseFormat.format('parent__'*parentLevel)] = param.pop()
        return Taxonomy.objects.filter(**filters)

def __processTaxonomyQuerysetParentID(param):
    """Process GET request parameters for parent by ID
    """
    return Taxonomy.objects.filter(parent__id = param) if param is not '0' else Taxonomy.objects.filter(parent__isnull=True)
    

def __processTaxonomyQuerysetToJSON(queryset):
    """Changes queryset to JSON for jsTree to use
    """
    
    json_data = []
    queryset = natsorted(queryset, lambda x: x.fullname)
    for taxonomy in queryset:
        node_id = str(taxonomy.id)
        node_parent = str(taxonomy.parent_id) if taxonomy.parent_id is not None else '#'
        node_text = str(taxonomy)
        json_data.append(dict(id=node_id, parent=node_parent, text=node_text))
    return json_data






