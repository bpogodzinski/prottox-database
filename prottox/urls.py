from django.urls import path
from prottox.views import browse_view, research_browser

urlpatterns = [
    path("", browse_view, name="browse_view"),
    path("research_browser/", research_browser, name="research_view"),
]
