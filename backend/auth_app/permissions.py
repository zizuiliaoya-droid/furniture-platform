"""Custom permission classes."""
from functools import wraps

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Only allow admin-level users (ADMIN / SUPER_ADMIN)."""
    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, 'is_admin', False))


def has_module_permission(user, module: str, action: str) -> bool:
    """查询角色权限矩阵。管理员级别默认全允许。"""
    if not user or not user.is_authenticated:
        return False
    if getattr(user, 'is_admin', False):
        return True
    from .models import RolePermission
    if not RolePermission.objects.filter(role=user.role).exists():
        from .services import PermissionMatrixService
        PermissionMatrixService.ensure_seeded()
    return RolePermission.objects.filter(
        role=user.role, module=module, action=action, allowed=True
    ).exists()


def require_module_permission(module: str, action: str):
    """为 DRF 函数式视图补充模块 × 操作硬校验。"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not has_module_permission(request.user, module, action):
                raise PermissionDenied(f'缺少{module}.{action}权限')
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


class HasModulePermission(BasePermission):
    """基于角色权限矩阵校验请求动作；视图需设置 module_name。"""
    ACTION_MAP = {
        'GET': 'view', 'HEAD': 'view', 'OPTIONS': 'view',
        'POST': 'create', 'PUT': 'update', 'PATCH': 'update', 'DELETE': 'delete',
    }

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'is_admin', False):
            return True
        module = getattr(view, 'module_name', None)
        if not module:
            return True
        action_map = getattr(view, 'permission_action_map', {})
        view_action = getattr(view, 'action', '')
        mapped_action = action_map.get(view_action)
        if isinstance(mapped_action, dict):
            action = mapped_action.get(request.method, self.ACTION_MAP.get(request.method, 'view'))
        else:
            action = mapped_action or self.ACTION_MAP.get(request.method, 'view')
        return has_module_permission(user, module, action)
