"""Persistent audit records for machine-initiated business actions."""
from django.conf import settings
from django.db import models


class AgentActionAudit(models.Model):
    class Status(models.TextChoices):
        SUCCEEDED = 'SUCCEEDED', '成功'
        FAILED = 'FAILED', '失败'
        DENIED = 'DENIED', '拒绝'

    request_id = models.CharField(max_length=64, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='agent_action_audits',
    )
    skill_name = models.CharField(max_length=100, default='unknown')
    action = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=12, choices=Status.choices)
    input_summary = models.JSONField(default=dict, blank=True)
    output_summary = models.JSONField(default=dict, blank=True)
    object_type = models.CharField(max_length=100, blank=True, default='')
    object_id = models.CharField(max_length=100, blank=True, default='')
    duration_ms = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['skill_name', '-created_at']),
        ]

    def __str__(self):
        return f'{self.skill_name}:{self.action}:{self.status}'
