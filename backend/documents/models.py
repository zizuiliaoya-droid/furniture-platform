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
    RESOURCE_TYPE_CHOICES = [
        ('FILE', '文件'),
        ('RICH_TEXT', '富文本'),
        ('VIDEO', '视频'),
        ('AUDIO', '音频'),
    ]
    name = models.CharField(max_length=300)
    doc_type = models.CharField(max_length=15, choices=DocumentFolder.DOC_TYPE_CHOICES)
    resource_type = models.CharField(max_length=15, choices=RESOURCE_TYPE_CHOICES, default='FILE',
                                     help_text='资源类型：文件/富文本/视频/音频')
    content = models.TextField(blank=True, default='', help_text='富文本内容（resource_type=RICH_TEXT 时使用）')
    folder = models.ForeignKey(DocumentFolder, null=True, blank=True, on_delete=models.SET_NULL, related_name='documents')
    file_path = models.CharField(max_length=500, blank=True, default='')
    file_size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True, default='')
    tags = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
