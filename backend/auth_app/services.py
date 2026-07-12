"""Authentication service."""
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from .models import User


class AuthService:
    @staticmethod
    def login(username: str, password: str) -> dict:
        user = User.objects.filter(username=username).first()
        if not user:
            raise ValueError('用户名或密码错误')
        if not user.is_active:
            raise ValueError('账号已被禁用，请联系管理员')
        if not user.check_password(password):
            raise ValueError('用户名或密码错误')
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        return {'token': token.key, 'user': user}

    @staticmethod
    def logout(user) -> None:
        Token.objects.filter(user=user).delete()

    @staticmethod
    def toggle_status(user_id: int) -> User:
        user = User.objects.get(pk=user_id)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        if not user.is_active:
            Token.objects.filter(user=user).delete()
        return user

    @staticmethod
    def reset_password(user_id: int, new_password: str) -> None:
        user = User.objects.get(pk=user_id)
        user.set_password(new_password)
        user.save()
        Token.objects.filter(user=user).delete()


# ─── AUTH-3 角色权限矩阵服务 ─────────────────────────────────────────────────

class PermissionMatrixService:
    """角色权限矩阵：模块 × 操作 → 是否允许。"""

    # 各角色默认权限（首次初始化用；之后由管理员在界面调整）
    DEFAULTS = {
        'SUPER_ADMIN': 'ALL',
        'ADMIN': 'ALL',
        'DEPT_MANAGER': {
            'PRODUCT': ['view', 'export'],
            'CATALOG': ['view'],
            'CASE': ['view', 'create', 'update'],
            'DOCUMENT': ['view', 'create'],
            'QUOTE': ['view', 'create', 'update', 'delete', 'export', 'share'],
            'PERMISSION': [],
        },
        'STAFF': {
            'PRODUCT': ['view'],
            'CATALOG': ['view'],
            'CASE': ['view'],
            'DOCUMENT': ['view'],
            'QUOTE': ['view', 'create', 'update', 'export'],
            'PERMISSION': [],
        },
    }

    @staticmethod
    def _model():
        from .models import RolePermission
        return RolePermission

    @classmethod
    def ensure_seeded(cls):
        RolePermission = cls._model()
        for role in RolePermission.ROLES:
            for module in RolePermission.MODULES:
                for action in RolePermission.ACTIONS:
                    default = cls._default_allowed(role, module, action)
                    RolePermission.objects.get_or_create(
                        role=role, module=module, action=action,
                        defaults={'allowed': default},
                    )

    @classmethod
    def _default_allowed(cls, role, module, action) -> bool:
        spec = cls.DEFAULTS.get(role, {})
        if spec == 'ALL':
            return True
        return action in spec.get(module, [])

    @classmethod
    def get_matrix(cls) -> dict:
        cls.ensure_seeded()
        RolePermission = cls._model()
        matrix = {}
        for rp in RolePermission.objects.all():
            matrix.setdefault(rp.role, {}).setdefault(rp.module, {})[rp.action] = rp.allowed
        return {
            'roles': RolePermission.ROLES,
            'modules': RolePermission.MODULES,
            'actions': RolePermission.ACTIONS,
            'matrix': matrix,
        }

    @classmethod
    def update_matrix(cls, items: list):
        """items: [{role, module, action, allowed}, ...]"""
        RolePermission = cls._model()
        for it in items:
            role, module, action = it.get('role'), it.get('module'), it.get('action')
            if role in ('ADMIN', 'SUPER_ADMIN'):
                continue  # 管理员级别恒为全允许，不可改
            if not (role and module and action):
                continue
            RolePermission.objects.update_or_create(
                role=role, module=module, action=action,
                defaults={'allowed': bool(it.get('allowed'))},
            )

    @classmethod
    def effective_for(cls, user) -> dict:
        """返回某用户角色的 {module: [allowed actions]}。管理员级别=全允许。"""
        RolePermission = cls._model()
        if getattr(user, 'is_admin', False):
            return {m: list(RolePermission.ACTIONS) for m in RolePermission.MODULES}
        cls.ensure_seeded()
        result = {}
        for rp in RolePermission.objects.filter(role=user.role, allowed=True):
            result.setdefault(rp.module, []).append(rp.action)
        return result
