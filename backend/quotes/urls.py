"""Quotes URL configuration."""
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('quotes', views.QuoteViewSet, basename='quote')

urlpatterns = [
    path('quotes/<int:quote_pk>/items/', views.QuoteItemViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('quotes/items/<int:pk>/', views.QuoteItemViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
] + router.urls
