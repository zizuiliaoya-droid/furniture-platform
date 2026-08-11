"""Agent 报价草稿的幂等和确定性定价测试。"""
from decimal import Decimal

import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from auth_app.models import RolePermission
from quotes.models import Quote


def agent_client(user):
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Token {token.key}',
        HTTP_X_AGENT_SKILL='furniture-quotes',
    )
    return client


def quote_payload(product):
    return {
        'title': '总部办公家具报价',
        'customer_name': '示例客户',
        'notes': '由 Agent 生成的草稿，待销售确认',
        'discount': '5.00',
        'items': [{
            'product_id': product.id,
            'selections': {'color': 'red', 'size': 'L'},
            'quantity': 2,
        }],
    }


@pytest.mark.django_db
class TestAgentQuoteDraftWorkflow:
    def test_idempotency_key_is_required(self, admin_user, product_matrix):
        response = agent_client(admin_user).post(
            '/api/agent/quotes/drafts/',
            quote_payload(product_matrix),
            format='json',
        )

        assert response.status_code == 400
        assert Quote.objects.count() == 0

    def test_draft_uses_server_price_and_is_idempotent(
        self,
        admin_user,
        product_matrix,
        settings,
    ):
        settings.PUBLIC_WEB_URL = 'https://furniture.example.com'
        client = agent_client(admin_user)
        headers = {'HTTP_IDEMPOTENCY_KEY': 'quote-demo-001'}

        first = client.post(
            '/api/agent/quotes/drafts/',
            quote_payload(product_matrix),
            format='json',
            **headers,
        )
        second = client.post(
            '/api/agent/quotes/drafts/',
            quote_payload(product_matrix),
            format='json',
            **headers,
        )

        assert first.status_code == 201
        assert second.status_code == 200
        assert second.data['replayed'] is True
        assert first.data['quote']['id'] == second.data['quote']['id']
        assert Quote.objects.count() == 1
        quote = Quote.objects.get()
        assert quote.status == 'DRAFT'
        assert quote.items.count() == 1
        item = quote.items.get()
        assert item.unit_price == Decimal('2580')
        assert item.quantity == 2
        assert quote.total_amount == Decimal('4902.00')
        assert first.data['web_url'] == f'https://furniture.example.com/quotes/{quote.id}'

    def test_same_key_with_different_payload_conflicts(self, admin_user, product_matrix):
        client = agent_client(admin_user)
        headers = {'HTTP_IDEMPOTENCY_KEY': 'quote-conflict-001'}
        payload = quote_payload(product_matrix)
        assert client.post(
            '/api/agent/quotes/drafts/', payload, format='json', **headers,
        ).status_code == 201
        payload['customer_name'] = '另一个客户'

        response = client.post(
            '/api/agent/quotes/drafts/', payload, format='json', **headers,
        )

        assert response.status_code == 409
        assert Quote.objects.count() == 1

    def test_invalid_item_rolls_back_whole_draft(self, admin_user, product_matrix):
        payload = quote_payload(product_matrix)
        payload['items'][0]['selections']['color'] = 'invalid'

        response = agent_client(admin_user).post(
            '/api/agent/quotes/drafts/',
            payload,
            format='json',
            HTTP_IDEMPOTENCY_KEY='quote-invalid-001',
        )

        assert response.status_code == 400
        assert Quote.objects.count() == 0

    def test_create_permission_is_enforced(self, staff_user, product_matrix):
        RolePermission.objects.create(
            role='STAFF', module='QUOTE', action='create', allowed=False,
        )

        response = agent_client(staff_user).post(
            '/api/agent/quotes/drafts/',
            quote_payload(product_matrix),
            format='json',
            HTTP_IDEMPOTENCY_KEY='quote-denied-001',
        )

        assert response.status_code == 403
        assert Quote.objects.count() == 0
