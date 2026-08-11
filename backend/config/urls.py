"""Root URL configuration."""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from common.views import health_view

urlpatterns = [
    path('api/health/', health_view, name='health'),
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
    path('api/agent/', include('agent_gateway.urls')),
]

# 始终服务媒体文件（测试环境 DEBUG=False 时也能访问上传图片）。
# 生产/大规模场景建议改由 nginx/对象存储直接服务。
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
