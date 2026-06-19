"""Sharing models."""
import uuid
from django.conf import settings
from django.db import models


class ShareLink(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('PRODUCT', '产品'),
        ('CASE', '案例'),
        ('QUOTE', '报价单'),
        ('CATALOG', '产品图册'),
        ('BATCH', '批量分享'),
    ]
    token = models.CharField(max_length=64, unique=True, db_index=True, default=uuid.uuid4)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)
    object_id = models.IntegerField(null=True, blank=True, help_text='单对象分享时使用')
    object_ids = models.JSONField(default=list, blank=True,
                                  help_text='批量分享时使用，如 [1,2,3]')
    title = models.CharField(max_length=200)
    password_hash = models.CharField(max_length=128, blank=True, default='')
    expires_at = models.DateTimeField(null=True, blank=True)
    max_access_count = models.IntegerField(null=True, blank=True)
    access_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.token[:8]}...)"


class ShareAccessLog(models.Model):
    share_link = models.ForeignKey(ShareLink, on_delete=models.CASCADE, related_name='access_logs')
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=45, blank=True, default='')
    user_agent = models.CharField(max_length=500, blank=True, default='')


class ClickTrackingLog(models.Model):
    share_link = models.ForeignKey(ShareLink, on_delete=models.CASCADE, related_name='click_logs')
    event_type = models.CharField(max_length=20)
    object_id = models.IntegerField()
    object_name = models.CharField(max_length=200, blank=True, default='')
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=45, blank=True, default='')


class BrandingConfig(models.Model):
    """分享页品牌展示配置（全局单例）"""
    company_name = models.CharField(max_length=200, default='')
    logo_path = models.CharField(max_length=500, blank=True, default='')
    contact_info = models.TextField(blank=True, default='',
                                    help_text='联系方式（电话/邮箱/地址等）')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '品牌展示配置'
        verbose_name_plural = '品牌展示配置'

    def __str__(self):
        return self.company_name or '品牌配置'
