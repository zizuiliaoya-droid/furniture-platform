"""Catalog URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path('catalog/', views.CatalogBrowseView.as_view(), name='catalog-browse'),
    path('catalog/search/', views.CatalogSearchView.as_view(), name='catalog-search'),
]
