"""Case models."""
from django.conf import settings
from django.db import models


class Case(models.Model):
    INDUSTRY_CHOICES = [
        ('TECH', '科技/互联网'),
        ('FINANCE', '金融/保险/财税'),
        ('REALESTATE', '地产/建筑/设计院'),
        ('EDUCATION', '教育培训'),
        ('MEDICAL', '医疗/大健康'),
        ('MEDIA', '广告/文创/传媒'),
        ('MANUFACTURE', '制造/实业/工厂'),
        ('GOVERNMENT', '政府/国企/事业单位'),
        ('OTHER', '其他'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    products = models.ManyToManyField('products.Product', through='CaseProduct', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CaseImage(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='images')
    image_path = models.CharField(max_length=500)
    thumbnail_path = models.JSONField(default=dict, blank=True)
    sort_order = models.IntegerField(default=0)
    is_cover = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']


class CaseProduct(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('case', 'product')
