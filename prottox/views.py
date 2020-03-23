from collections import Counter, OrderedDict
from heapq import nlargest
import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import Toxin_research, SpeciesTaxonomy, FactorTaxonomy

def home_view(request):
    context = {}
    context['page_content_template_name'] = 'home.html'
    context['header'] = 'Home'

    queryset = Toxin_research.objects.all()
    context['maxItems'] = queryset.count()

    researchInteractions = Counter([x.results.interaction for x in queryset])
    context['research'] = {'interactions': researchInteractions,
                           'sum': sum(researchInteractions.values())}

    countedSpecies = __countSpecies(SpeciesTaxonomy.objects.filter(taxonomy_rank__name='Species'))
    context['target'] = {'species': OrderedDict(sorted(dict(countedSpecies).items())),
                         'speciesJSON': json.dumps(countedSpecies),
                         'sum': sum(countedSpecies.values())}

    allFactors = {k.name :v for k, v in __getTaxCount().items()}
    context['factors'] = {'allFactors': allFactors,
                          'allFactorsJSON': json.dumps(allFactors),
                          '4largestJSON': json.dumps(nlargest(4, allFactors, key=allFactors.get)),
                          'sum': sum(allFactors.values())}

    return render(request, "home.html", context)

def organism_browse_view(request):
    """Browsing page view"""
    return render(request, "organism_browse.html", {'page_content_template_name':'browse.html', 'header': 'Organism Browser'})

def factor_browse_view(request):
    """Browsing page view"""
    return render(request, "factor_browse.html", {'page_content_template_name':'browse.html', 'header': 'Toxin Browser'})


def research_browser_view(request):
    """Research browser page view. This view is
    supposed to show user researches that included chosen factors/taxonomies
    in POST request

    Arguments:
        request.POST['IDs'] {string} -- string of ID's sepatated with ","
        containing ID's of interest.
        request.POST['entity'] {string} -- string containing name of the table
        that it came from. Can be 'factor' or 'taxonomy'

    Returns:
        render('research.html') -- researches that have particular ID's in it
        redirect to factor_browse_view -- if there isn't any ID's in POST
    """
    if request.POST.get("IDs", None):
        IDs = request.POST["IDs"].strip().split(",")
        database = request.POST["entity"]
        return render(request, "research_browser.html",
                      {"IDs":IDs, "table":database,
                       'page_content_template_name':'research_browser.html',
                       'header': 'Research Browser'})
    else:
        return redirect("factor_browse_view")

def compare_research_view(request):
    ids = request.GET["IDs"].split(",")
    return render(request, "compare.html", {"IDs":ids, 'page_content_template_name':'compare.html','header': 'Compare Research'})

def research_view(request, db_id=1):
    research = get_object_or_404(Toxin_research, pk=db_id)
    return render(request, 'research.html',
                  {'research':research, 'synfactor':__roundOrEmptyString(research.results.synergism_factor, 2), 'page_content_template_name':'research.html', 'header': 'Research View'})

# PROCESSING METHODS

def __countSpecies(species):
    return Counter(map(__getOrder, species))

def __getOrder(item):
    if item.taxonomy_rank.name != 'Order':
        return __getOrder(item.parent)
    return item.name

def __roundOrEmptyString(number, ndigits=None):
    try:
        return round(float(number.replace(',','.')), ndigits)
    except ValueError:
        return ''

def __getTaxCount():
    leaves = FactorTaxonomy.objects.filter(children__isnull=True)
    return Counter(map(__getTopParent, leaves))

def __getTopParent(tax):
    if tax.parent is not None:
        return __getTopParent(tax.parent)
    else:
        return tax