from django.shortcuts import render, redirect
from prottox.models import Toxin_research


def browse_view(request):
    """Landing page view"""
    return render(request, "browse.html", {})


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
    if request.POST.get("IDs", None):
        IDs = request.POST["IDs"].strip().split(",")
        database = request.POST["entity"]
            
        return render(request, "research_browser.html", {"IDs":IDs, "table":database})
    else:
        return redirect("browse_view")
