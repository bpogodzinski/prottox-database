from django.urls import path, include
from . import views

urlpatterns = [
    path('factortaxonomy/', views.factorTaxonomyAPI),
    path('targettaxonomy/', views.targetTaxonomyAPI)
]
