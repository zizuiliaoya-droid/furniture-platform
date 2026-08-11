import pytest
from django.core.cache import cache
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_login_is_rate_limited_after_repeated_failures():
    cache.clear()
    client = APIClient()

    responses = [
        client.post(
            '/api/auth/login/',
            {'username': 'missing', 'password': 'not-the-password'},
            format='json',
        )
        for _ in range(11)
    ]

    assert all(response.status_code == 400 for response in responses[:10])
    assert responses[-1].status_code == 429
    cache.clear()


@pytest.mark.django_db
def test_new_user_password_requires_twelve_characters(admin_user):
    client = APIClient()
    client.force_authenticate(admin_user)

    response = client.post(
        '/api/auth/users/',
        {
            'username': 'weak-password-user',
            'password': 'short123',
            'display_name': '弱密码账号',
            'role': 'STAFF',
        },
        format='json',
    )

    assert response.status_code == 400
    assert 'password' in response.json()
