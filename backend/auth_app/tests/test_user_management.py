"""用户角色与超级管理员保护回归测试。"""
import pytest
from rest_framework.test import APIClient

from auth_app.models import User


def client_for(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def super_admin(db):
    return User.objects.create_user(
        username='root', password='root123456', role='SUPER_ADMIN',
        display_name='超级管理员', is_active=True,
    )


@pytest.mark.django_db
class TestUserManagement:
    def test_admin_cannot_promote_super_admin(self, admin_user, staff_user):
        response = client_for(admin_user).patch(
            f'/api/auth/users/{staff_user.id}/', {'role': 'SUPER_ADMIN'}, format='json')
        assert response.status_code == 400
        staff_user.refresh_from_db()
        assert staff_user.role == 'STAFF'

    def test_cannot_remove_last_active_super_admin(self, super_admin):
        response = client_for(super_admin).patch(
            f'/api/auth/users/{super_admin.id}/', {'is_active': False}, format='json')
        assert response.status_code == 400
        super_admin.refresh_from_db()
        assert super_admin.is_active is True

    def test_admin_cannot_reset_super_admin_password(self, admin_user, super_admin):
        response = client_for(admin_user).post(
            f'/api/auth/users/{super_admin.id}/reset-password/',
            {'new_password': 'newpass123'}, format='json')
        assert response.status_code == 403

    def test_admin_cannot_deactivate_self_through_generic_patch(self, admin_user):
        response = client_for(admin_user).patch(
            f'/api/auth/users/{admin_user.id}/', {'is_active': False}, format='json')
        assert response.status_code == 400
        admin_user.refresh_from_db()
        assert admin_user.is_active is True