"""Auth app URL configuration."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.me_view, name='me'),
    path('users/<int:pk>/toggle-status/', views.toggle_user_status, name='toggle-user-status'),
    path('users/<int:pk>/reset-password/', views.reset_user_password, name='reset-user-password'),
] + router.urls
