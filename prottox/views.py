from django.shortcuts import render, redirect


def browse_view(request):
    """Browsing page view"""
    return render(request, "browse.html", {'page_content_template_name':'factors_browser.html'})


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
        redirect to home_view -- if there isn't any ID's in POST
    """
    if request.POST.get("IDs", None):
        IDs = request.POST["IDs"].strip().split(",")
        database = request.POST["entity"]
            
        return render(request, "research_browser.html", {"IDs":IDs, "table":database, 'page_content_template_name':'research_browser.html'})
    else:
        return redirect("browse_view")

def compare_research_view(request):
    ids = request.GET["IDs"].split(",")

    return render(request, "compare.html", {"IDs":ids, 'page_content_template_name':'compare.html'})