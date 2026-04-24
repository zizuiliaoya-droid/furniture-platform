"""Search URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.global_search_view, name='global-search'),
]
