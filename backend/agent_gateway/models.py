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


class AgentIdempotencyRecord(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', '处理中'
        SUCCEEDED = 'SUCCEEDED', '成功'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agent_idempotency_records',
    )
    action = models.CharField(max_length=100)
    key = models.CharField(max_length=128)
    request_digest = models.CharField(max_length=64)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    response_data = models.JSONField(default=dict, blank=True)
    object_type = models.CharField(max_length=100, blank=True, default='')
    object_id = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'action', 'key'],
                name='unique_agent_idempotency_key',
            ),
        ]


class AgentConfirmationUse(models.Model):
    token_digest = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='agent_confirmation_uses',
    )
    action = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100)
    request_id = models.CharField(max_length=64)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-used_at', '-id']
