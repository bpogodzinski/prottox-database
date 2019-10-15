from collections import Counter, OrderedDict
from random import choice
import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import Toxin_research, Active_factor, Factor_source, Target, SpeciesTaxonomy

def home_view(request):
    queryset = Toxin_research.objects.all()
    countInteraction = Counter([x.results.interaction for x in queryset])
    countFactors = Active_factor.objects.all().distinct().count()
    countChimeric = Active_factor.objects.filter(is_chimeric=True).distinct().count()
    countNotToxin = Active_factor.objects.filter(is_toxin=False).distinct().count()
    countSource = Factor_source.objects.all().distinct().count()
    counted = __countSpecies(SpeciesTaxonomy.objects.filter(taxonomy_rank__name='Species'))
    countSpeciesDict = OrderedDict(sorted(dict(counted).items()))
    print(countSpeciesDict)
    countSpecies = json.dumps(counted)

    return render(request, "home.html",
                  {'page_content_template_name':'home.html',
                   'header': 'Home',
                   'countInteraction':countInteraction,
                   'countFactors':countFactors,
                   'countChimeric':countChimeric,
                   'countNotToxin':countNotToxin,
                   'sumResearch':sum(countInteraction.values()),
                   'randomResearch':choice(queryset),
                   'countSource':countSource,
                   'countSpecies': countSpecies,
                   'species': countSpeciesDict,
    })

def organism_browse_view(request):
    """Browsing page view"""
    return render(request, "organism_browse.html", {'page_content_template_name':'browse.html','header': 'Organism Browser'})

def factor_browse_view(request):
    """Browsing page view"""
    return render(request, "factor_browse.html", {'page_content_template_name':'browse.html', 'header': 'Factor Browser'})


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
    return render(request, "compare.html", {"IDs":ids, 'page_content_template_name':'compare.html','header': 'Compare research'})

def research_view(request, db_id):
    research = get_object_or_404(Toxin_research, pk=db_id)
    return render(request, 'research.html',
                  {'research':research, 'page_content_template_name':'research.html', 'header': 'Research view'})

# PROCESSING METHODS

def __countSpecies(species):
    return Counter(map(__getOrder, species))

def __getOrder(item):
    if item.taxonomy_rank.name != 'Order':
        return __getOrder(item.parent)
    return item.name