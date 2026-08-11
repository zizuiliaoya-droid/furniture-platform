"""Agent capability registry and audit helpers."""
from dataclasses import asdict, dataclass
from decimal import Decimal
from time import perf_counter
import hashlib
import json
import re
from uuid import UUID, uuid4

from django.conf import settings
from django.core import signing
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError, transaction

from .models import (
    AgentActionAudit,
    AgentConfirmationUse,
    AgentIdempotencyRecord,
)


SENSITIVE_KEY_PARTS = (
    'password', 'passwd', 'secret', 'token', 'authorization', 'cookie',
    'session', 'credential', 'private_key',
)
MAX_AUDIT_TEXT = 1000
MAX_AUDIT_ITEMS = 50
MAX_AUDIT_DEPTH = 5


def _is_sensitive_key(key):
    normalized = str(key).casefold().replace('-', '_')
    return any(part in normalized for part in SENSITIVE_KEY_PARTS)


def sanitize_for_audit(value, *, _depth=0):
    """Return a bounded JSON-safe copy with credentials removed."""
    if _depth >= MAX_AUDIT_DEPTH:
        return '[TRUNCATED]'
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    if isinstance(value, bytes):
        return f'[BINARY {len(value)} bytes]'
    if isinstance(value, str):
        return value if len(value) <= MAX_AUDIT_TEXT else value[:MAX_AUDIT_TEXT] + '…'
    if isinstance(value, dict):
        sanitized = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= MAX_AUDIT_ITEMS:
                sanitized['__truncated__'] = True
                break
            sanitized[str(key)] = (
                '[REDACTED]' if _is_sensitive_key(key)
                else sanitize_for_audit(item, _depth=_depth + 1)
            )
        return sanitized
    if isinstance(value, (list, tuple, set)):
        items = list(value)
        sanitized = [
            sanitize_for_audit(item, _depth=_depth + 1)
            for item in items[:MAX_AUDIT_ITEMS]
        ]
        if len(items) > MAX_AUDIT_ITEMS:
            sanitized.append('[TRUNCATED]')
        return sanitized
    return sanitize_for_audit(str(value), _depth=_depth + 1)


def agent_request_id(request):
    candidate = str(request.headers.get('X-Request-ID') or '').strip()
    try:
        return str(UUID(candidate)) if candidate else str(uuid4())
    except (ValueError, AttributeError):
        return str(uuid4())


def agent_skill_name(request):
    raw = str(request.headers.get('X-Agent-Skill') or 'unknown').strip()
    safe = re.sub(r'[^A-Za-z0-9_.-]+', '-', raw).strip('-')
    return (safe or 'unknown')[:100]


def record_agent_audit(
    *, request, request_id, action, status, started_at,
    input_data=None, output_data=None, object_type='', object_id='',
):
    elapsed = max(0, round((perf_counter() - started_at) * 1000))
    return AgentActionAudit.objects.create(
        request_id=request_id,
        user=request.user,
        skill_name=agent_skill_name(request),
        action=action,
        status=status,
        input_summary=sanitize_for_audit(input_data or {}),
        output_summary=sanitize_for_audit(output_data or {}),
        object_type=str(object_type or '')[:100],
        object_id=str(object_id or '')[:100],
        duration_ms=elapsed,
    )


@dataclass(frozen=True)
class AgentCapability:
    name: str
    description: str
    method: str
    path: str
    mode: str
    required_permission: str = ''
    requires_confirmation: bool = False

    def as_dict(self):
        return asdict(self)


CAPABILITIES = (
    AgentCapability(
        name='system_capabilities',
        description='查询当前账号可使用的 Agent 工具和调用约束',
        method='GET',
        path='/api/agent/capabilities/',
        mode='read',
    ),
    AgentCapability(
        name='product_search',
        description='按关键词、分类、品牌、产地、货期和价格范围搜索在售产品',
        method='GET',
        path='/api/agent/products/search/',
        mode='read',
        required_permission='CATALOG.view',
    ),
    AgentCapability(
        name='product_detail',
        description='查询单个产品、图片、配置维度和默认组合',
        method='GET',
        path='/api/agent/products/{product_id}/',
        mode='read',
        required_permission='PRODUCT.view',
    ),
    AgentCapability(
        name='price_calculate',
        description='使用后端确定性定价服务验证配置并计算价格',
        method='POST',
        path='/api/agent/products/{product_id}/price/',
        mode='read',
        required_permission='PRODUCT.view',
    ),
    AgentCapability(
        name='document_search',
        description='检索内部设计、培训和资质资料，返回受限摘要和页面链接',
        method='GET',
        path='/api/agent/documents/search/',
        mode='read',
        required_permission='DOCUMENT.view',
    ),
    AgentCapability(
        name='case_search',
        description='按关键词和行业检索案例及关联产品',
        method='GET',
        path='/api/agent/cases/search/',
        mode='read',
        required_permission='CASE.view',
    ),
    AgentCapability(
        name='quote_create_draft',
        description='按产品配置创建由后端定价的报价草稿；相同幂等键只创建一次',
        method='POST',
        path='/api/agent/quotes/drafts/',
        mode='draft',
        required_permission='QUOTE.create',
    ),
    AgentCapability(
        name='config_import_preview',
        description='解析配置 Excel、展示影响并签发短期确认票据，不修改数据',
        method='POST',
        path='/api/agent/products/{product_id}/config-import/preview/',
        mode='draft',
        required_permission='PRODUCT.update',
    ),
    AgentCapability(
        name='config_import_confirm',
        description='使用预览票据和完全相同的文件确认配置导入',
        method='POST',
        path='/api/agent/products/{product_id}/config-import/confirm/',
        mode='write',
        required_permission='PRODUCT.update',
        requires_confirmation=True,
    ),
)


def visible_capabilities(user):
    from auth_app.permissions import has_module_permission

    visible = []
    for capability in CAPABILITIES:
        if capability.required_permission:
            module, action = capability.required_permission.split('.', 1)
            if not has_module_permission(user, module, action):
                continue
        visible.append(capability.as_dict())
    return visible


def public_web_url():
    return str(getattr(settings, 'PUBLIC_WEB_URL', 'http://localhost')).rstrip('/')


def require_agent_permission(
    *, request, request_id, started_at, action, module, permission,
    input_data=None,
):
    """Enforce the existing permission matrix and audit authenticated denial."""
    from auth_app.permissions import has_module_permission
    from rest_framework.exceptions import PermissionDenied

    if has_module_permission(request.user, module, permission):
        return
    record_agent_audit(
        request=request,
        request_id=request_id,
        action=action,
        status=AgentActionAudit.Status.DENIED,
        started_at=started_at,
        input_data=input_data or {},
        output_data={'detail': f'缺少{module}.{permission}权限'},
    )
    raise PermissionDenied(f'缺少{module}.{permission}权限')


class IdempotencyConflict(ValueError):
    pass


class IdempotencyInProgress(ValueError):
    pass


class ConfirmationInvalid(ValueError):
    pass


class ConfirmationReplay(ValueError):
    pass


def canonical_digest(payload):
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(',', ':'),
        cls=DjangoJSONEncoder,
    ).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


@transaction.atomic
def run_idempotent(*, user, action, key, payload, operation):
    """Execute one transactional operation at most once per user/action/key."""
    request_digest = canonical_digest(payload)
    record, created = AgentIdempotencyRecord.objects.select_for_update().get_or_create(
        user=user,
        action=action,
        key=key,
        defaults={'request_digest': request_digest},
    )
    if not created:
        if record.request_digest != request_digest:
            raise IdempotencyConflict('该幂等键已用于不同请求，请更换幂等键')
        if record.status == AgentIdempotencyRecord.Status.SUCCEEDED:
            return record.response_data, True
        raise IdempotencyInProgress('相同请求正在处理中，请稍后重试')
    response_data, object_type, object_id = operation()
    record.status = AgentIdempotencyRecord.Status.SUCCEEDED
    record.response_data = response_data
    record.object_type = str(object_type or '')[:100]
    record.object_id = str(object_id or '')[:100]
    record.save(update_fields=[
        'status', 'response_data', 'object_type', 'object_id', 'updated_at',
    ])
    return response_data, False


CONFIRMATION_SALT = 'agent-gateway-confirmation-v1'


def import_request_digest(file_content, *, product_id, mapping, replace_dimensions, replace_prices):
    file_hash = hashlib.sha256(file_content).hexdigest()
    return canonical_digest({
        'file_sha256': file_hash,
        'product_id': product_id,
        'mapping': mapping or {},
        'replace_dimensions': bool(replace_dimensions),
        'replace_prices': bool(replace_prices),
    })


def issue_confirmation(*, user, action, resource_id, request_digest):
    return signing.dumps({
        'user_id': user.id,
        'action': action,
        'resource_id': str(resource_id),
        'request_digest': request_digest,
        'nonce': str(uuid4()),
    }, salt=CONFIRMATION_SALT, compress=True)


def verify_confirmation(*, token, user, action, resource_id, request_digest):
    try:
        payload = signing.loads(
            token,
            salt=CONFIRMATION_SALT,
            max_age=getattr(settings, 'AGENT_CONFIRMATION_MAX_AGE', 600),
        )
    except signing.SignatureExpired as exc:
        raise ConfirmationInvalid('确认票据已过期，请重新预览') from exc
    except signing.BadSignature as exc:
        raise ConfirmationInvalid('确认票据无效，请重新预览') from exc
    expected = {
        'user_id': user.id,
        'action': action,
        'resource_id': str(resource_id),
        'request_digest': request_digest,
    }
    if any(payload.get(key) != value for key, value in expected.items()):
        raise ConfirmationInvalid('确认票据与当前用户、文件或导入选项不匹配')
    return payload


def consume_confirmation(*, token, user, action, resource_id, request_id):
    token_digest = hashlib.sha256(token.encode('utf-8')).hexdigest()
    try:
        return AgentConfirmationUse.objects.create(
            token_digest=token_digest,
            user=user,
            action=action,
            resource_id=str(resource_id),
            request_id=request_id,
        )
    except IntegrityError as exc:
        raise ConfirmationReplay('确认票据已使用，不能重复执行') from exc
