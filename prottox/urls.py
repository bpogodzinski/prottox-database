from django.urls import path
from .views import organism_browse_view, factor_browse_view, research_browser_view, compare_research_view, research_view

urlpatterns = [
    path("factor_browser/", factor_browse_view, name="factor_browse_view"),
    path("organism_browser/", organism_browse_view, name="organism_browse_view"),
    path("research_browser/", research_browser_view, name="research_browser_view"),
    path("compare/", compare_research_view, name='compare_view'),
    path("research/<int:db_id>/", research_view, name='research_view')
]
