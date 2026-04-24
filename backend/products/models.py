"""Product management models."""
from django.conf import settings
from django.db import models


class Category(models.Model):
    DIMENSION_CHOICES = [
        ('TYPE', '按类型'),
        ('SPACE', '按空间'),
        ('ORIGIN', '按产地'),
    ]
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    dimension = models.CharField(max_length=10, choices=DIMENSION_CHOICES)
    sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('parent', 'name', 'dimension')
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Product(models.Model):
    ORIGIN_CHOICES = [
        ('IMPORT', '进口'),
        ('DOMESTIC', '国产'),
        ('CUSTOM', '定制'),
    ]
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='primary_products')
    origin = models.CharField(max_length=10, choices=ORIGIN_CHOICES)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    categories = models.ManyToManyField(Category, through='ProductCategory', related_name='products', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['origin']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'category')


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_path = models.CharField(max_length=500)
    thumbnail_path = models.JSONField(default=dict, blank=True)
    sort_order = models.IntegerField(default=0)
    is_cover = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']


class ProductConfig(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='configs')
    config_name = models.CharField(max_length=200)
    attributes = models.JSONField(default=dict, blank=True)
    guide_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.config_name}"
