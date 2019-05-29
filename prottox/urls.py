from django.urls import path
from prottox.views import home_view, research_browser

urlpatterns = [
    path("", home_view, name="home_view"),
    path("research_browser/", research_browser, name="research_browser"),
]
