from django.urls import path
from .views import browse_view, research_browser_view, compare_research_view

urlpatterns = [
    path("factor_browser/", browse_view, name="browse_view"),
    path("research_browser/", research_browser_view, name="research_view"),
    path("compare/", compare_research_view, name='compare_view'),
]
