from django.urls import path, include
from . import views

urlpatterns = [
    path('taxonomy/', views.taxonomyAPI),
    path('active_factor/', views.activeFactorAPI)
]
