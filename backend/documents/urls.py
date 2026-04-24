"""Documents URL configuration."""
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('document-folders', views.DocumentFolderViewSet, basename='document-folder')

urlpatterns = [
    path('documents/', views.DocumentViewSet.as_view({'get': 'list'}), name='document-list'),
    path('documents/upload/', views.upload_document, name='document-upload'),
    path('documents/<int:pk>/', views.DocumentViewSet.as_view({'delete': 'destroy'}), name='document-delete'),
    path('documents/<int:pk>/download/', views.download_document, name='document-download'),
    path('documents/<int:pk>/tags/', views.update_document_tags, name='document-tags'),
    path('document-folders/tree/', views.DocumentFolderViewSet.as_view({'get': 'tree'}), name='folder-tree'),
] + router.urls
