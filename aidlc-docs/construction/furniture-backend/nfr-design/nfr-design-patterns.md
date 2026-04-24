# NFR 设计模式 — Unit 1 后端

## 1. 性能模式

### P-01: 数据库查询优化
**模式**: Eager Loading + 索引优化

```python
# select_related: FK 关系（单次 JOIN 查询）
Product.objects.select_related('category', 'created_by')

# prefetch_related: M2M 和反向 FK（两次查询，Python 端合并）
Product.objects.prefetch_related('images', 'configs', 'categories')

# 组合使用
Quote.objects.select_related('created_by').prefetch_related('items__product')
```

**索引策略**:
```python
class Product(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['origin']),
            models.Index(fields=['-created_at']),
        ]

class Quote(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['-updated_at']),
        ]

class ShareLink(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['token']),  # 已有 UNIQUE 约束自带索引
        ]
```

### P-02: 分页模式
**模式**: Cursor-based 或 Offset-based 分页

```python
# 使用 DRF 标准分页（Offset-based，数据量小足够）
class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
```

### P-03: 文件处理模式
**模式**: 同步处理 + 流式上传

```python
# 图片上传流程
def upload_images(product_id, files):
    for file in files:
        # 1. 验证文件大小和类型
        validate_file(file, max_size=10*1024*1024)
        # 2. 保存原图
        path = file_storage.upload(file, 'products')
        # 3. 同步生成缩略图
        thumb_small = file_storage.generate_thumbnail(path, (150, 150))
        thumb_medium = file_storage.generate_thumbnail(path, (400, 400))
        # 4. 创建数据库记录
        ProductImage.objects.create(...)
```

---

## 2. 安全模式

### S-01: 认证中间件模式
**模式**: Token Authentication + 自定义权限类

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# permissions.py
class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'ADMIN'

# views.py — 管理员操作
class ProductViewSet(ModelViewSet):
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]
```

### S-02: CORS 白名单模式
```python
# settings.py
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
CORS_ALLOW_CREDENTIALS = True
```

### S-03: 文件访问安全模式
**模式**: 间接访问（生产环境通过 Nginx 代理）

```
# 生产环境：Nginx 代理媒体文件
location /media/ {
    alias /app/media/;
    # 不暴露目录列表
    autoindex off;
}

# 测试环境：Django 直接服务（开发便利）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 3. 可靠性模式

### R-01: 全局异常处理模式
**模式**: DRF Custom Exception Handler

```python
# common/exceptions.py
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        # 未捕获异常 → 500
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return Response({'detail': 'Internal server error'}, status=500)
    return response
```

### R-02: 数据库事务模式
**模式**: 关键操作使用 atomic 事务

```python
from django.db import transaction

# 报价复制（多表操作需要事务）
@transaction.atomic
def duplicate(quote_id, user):
    quote = Quote.objects.get(id=quote_id)
    new_quote = Quote.objects.create(...)
    for item in quote.items.all():
        QuoteItem.objects.create(quote=new_quote, ...)
    new_quote.recalculate_total()
    return new_quote

# Excel 批量导入
@transaction.atomic
def execute_import(parsed_data):
    products = [Product(**data) for data in parsed_data]
    Product.objects.bulk_create(products)
```

### R-03: 容器自愈模式
```yaml
# docker-compose.yml
services:
  backend:
    restart: always
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/api/health/')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 4. 配置管理模式

### C-01: 环境变量驱动配置
**模式**: 12-Factor App 配置

```python
# settings.py
import dj_database_url

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# 数据库：优先 DATABASE_URL（Railway），否则用 DB_* 变量
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'furniture_app'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
```

### C-02: 静态文件服务模式
```python
# Railway 环境：WhiteNoise
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 静态文件
    ...
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```
