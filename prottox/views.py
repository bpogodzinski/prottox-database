from django.shortcuts import render, redirect
from prottox.models import Toxin_research

def home_view(request):
    """Landing page view"""
    return render(request, 'home.html', {})

def research_browser(request):
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
        redirect to home_view -- if there isn't any ID's in POST
    """
    if request.POST.get('IDs', None):
        IDs = request.POST['IDs'].strip().split(',')
        database = request.POST['entity']

        if database == 'factor':
            queryset = Toxin_research.objects.filter(toxin__taxonomy__in=IDs).distinct()
        else:
            queryset = Toxin_research.objects.filter(target__target_organism_taxonomy__in=IDs).distinct()

        return render(request, 'research_browser.html', {'ids':IDs, 'table':database, 'data':queryset})
    else:
        return redirect('home_view')
