"""Agent capability registry and audit helpers."""
from dataclasses import asdict, dataclass
from decimal import Decimal
from time import perf_counter
import re
from uuid import UUID, uuid4

from django.conf import settings

from .models import AgentActionAudit


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
