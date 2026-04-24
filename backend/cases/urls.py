"""Cases URL configuration."""
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('cases', views.CaseViewSet, basename='case')

urlpatterns = [
    path('cases/images/<int:pk>/', views.delete_case_image),
] + router.urls
