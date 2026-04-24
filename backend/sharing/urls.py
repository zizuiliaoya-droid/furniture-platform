"""Sharing URL configuration."""
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('shares', views.ShareLinkViewSet, basename='share')

urlpatterns = [
    path('share/<str:token>/', views.share_content_view, name='share-content'),
    path('share/<str:token>/verify/', views.share_verify_view, name='share-verify'),
    path('share/<str:token>/track/', views.share_track_click, name='share-track'),
] + router.urls
