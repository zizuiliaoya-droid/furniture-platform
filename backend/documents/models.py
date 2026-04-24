"""Document models."""
from django.conf import settings
from django.db import models


class DocumentFolder(models.Model):
    DOC_TYPE_CHOICES = [
        ('DESIGN', '设计资源'),
        ('TRAINING', '培训资料'),
        ('CERTIFICATE', '资质文件'),
    ]
    name = models.CharField(max_length=200)
    doc_type = models.CharField(max_length=15, choices=DOC_TYPE_CHOICES)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Document(models.Model):
    name = models.CharField(max_length=300)
    doc_type = models.CharField(max_length=15, choices=DocumentFolder.DOC_TYPE_CHOICES)
    folder = models.ForeignKey(DocumentFolder, null=True, blank=True, on_delete=models.SET_NULL, related_name='documents')
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
