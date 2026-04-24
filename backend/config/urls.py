"""Root URL configuration."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('auth_app.urls')),
    path('api/', include('products.urls')),
    path('api/', include('catalog.urls')),
    path('api/', include('cases.urls')),
    path('api/', include('documents.urls')),
    path('api/', include('quotes.urls')),
    path('api/', include('sharing.urls')),
    path('api/', include('search.urls')),
    path('api/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
