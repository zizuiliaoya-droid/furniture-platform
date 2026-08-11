# Generated for the initial Agent Gateway audit model.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentActionAudit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_id', models.CharField(db_index=True, max_length=64)),
                ('skill_name', models.CharField(default='unknown', max_length=100)),
                ('action', models.CharField(db_index=True, max_length=100)),
                ('status', models.CharField(choices=[('SUCCEEDED', '成功'), ('FAILED', '失败'), ('DENIED', '拒绝')], max_length=12)),
                ('input_summary', models.JSONField(blank=True, default=dict)),
                ('output_summary', models.JSONField(blank=True, default=dict)),
                ('object_type', models.CharField(blank=True, default='', max_length=100)),
                ('object_id', models.CharField(blank=True, default='', max_length=100)),
                ('duration_ms', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='agent_action_audits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at', '-id'],
                'indexes': [
                    models.Index(fields=['user', '-created_at'], name='agent_gatew_user_id_7f4483_idx'),
                    models.Index(fields=['skill_name', '-created_at'], name='agent_gatew_skill_n_b2b215_idx'),
                ],
            },
        ),
    ]
