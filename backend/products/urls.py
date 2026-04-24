"""Product app URL configuration."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet, basename='product')
router.register('categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('products/<int:product_pk>/configs/', views.ProductConfigViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('products/configs/<int:pk>/', views.ProductConfigViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
    path('products/images/<int:pk>/', views.delete_product_image),
    path('products/images/<int:pk>/cover/', views.set_cover_image),
] + router.urls
