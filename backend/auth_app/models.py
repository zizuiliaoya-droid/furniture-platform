"""User model extending AbstractUser with role and display_name."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    """部门（组织架构占位，AUTH-1；完整层级树待定后完善）"""
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', '超级管理员'),
        ('ADMIN', '管理员'),
        ('DEPT_MANAGER', '部门主管'),
        ('STAFF', '普通员工'),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='STAFF')
    display_name = models.CharField(max_length=100, blank=True, default='')
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='members')

    class Meta:
        db_table = 'auth_user'

    @property
    def is_admin(self) -> bool:
        """管理员级别（管理员 / 超级管理员）"""
        return self.role in ('ADMIN', 'SUPER_ADMIN')

    def __str__(self):
        return self.display_name or self.username


class RolePermission(models.Model):
    """角色权限矩阵（AUTH-3）：模块 × 操作 → 是否允许。"""
    MODULES = ['PRODUCT', 'CATALOG', 'CASE', 'DOCUMENT', 'QUOTE', 'PERMISSION']
    ACTIONS = ['view', 'create', 'update', 'delete', 'export', 'share']
    ROLES = ['SUPER_ADMIN', 'ADMIN', 'DEPT_MANAGER', 'STAFF']

    role = models.CharField(max_length=15)
    module = models.CharField(max_length=20)
    action = models.CharField(max_length=10)
    allowed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'module', 'action')
        ordering = ['role', 'module', 'action']

    def __str__(self):
        return f'{self.role}.{self.module}.{self.action}={self.allowed}'
