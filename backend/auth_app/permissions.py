"""Custom permission classes."""
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
    return RolePermission.objects.filter(
        role=user.role, module=module, action=action, allowed=True
    ).exists()


class HasModulePermission(BasePermission):
    """基于角色权限矩阵的对象级权限（视图需设置 module_name）。
    读操作（GET/HEAD/OPTIONS）映射 view；写操作映射 create/update/delete。
    """
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
        action = self.ACTION_MAP.get(request.method, 'view')
        return has_module_permission(user, module, action)
