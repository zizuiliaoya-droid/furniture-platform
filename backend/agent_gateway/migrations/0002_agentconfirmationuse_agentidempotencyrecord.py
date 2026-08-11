import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('agent_gateway', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentConfirmationUse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_digest', models.CharField(max_length=64, unique=True)),
                ('action', models.CharField(max_length=100)),
                ('resource_id', models.CharField(max_length=100)),
                ('request_id', models.CharField(max_length=64)),
                ('used_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='agent_confirmation_uses', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-used_at', '-id']},
        ),
        migrations.CreateModel(
            name='AgentIdempotencyRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=100)),
                ('key', models.CharField(max_length=128)),
                ('request_digest', models.CharField(max_length=64)),
                ('status', models.CharField(choices=[('PENDING', '处理中'), ('SUCCEEDED', '成功')], default='PENDING', max_length=12)),
                ('response_data', models.JSONField(blank=True, default=dict)),
                ('object_type', models.CharField(blank=True, default='', max_length=100)),
                ('object_id', models.CharField(blank=True, default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agent_idempotency_records', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='agentidempotencyrecord',
            constraint=models.UniqueConstraint(fields=('user', 'action', 'key'), name='unique_agent_idempotency_key'),
        ),
    ]
