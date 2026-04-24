"""Dashboard URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/stats/', views.dashboard_stats_view, name='dashboard-stats'),
]
