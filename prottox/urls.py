from django.urls import path
from .views import browse_view, research_browser_view, compare_research_view, research_view

urlpatterns = [
    path("factor_browser/", browse_view, name="browse_view"),
    path("research_browser/", research_browser_view, name="research_browser_view"),
    path("compare/", compare_research_view, name='compare_view'),
    path("research/<int:db_id>/", research_view, name='research_view')
]
