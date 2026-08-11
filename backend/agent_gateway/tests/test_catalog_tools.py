"""Agent 只读产品与算价工具测试。"""
from decimal import Decimal

import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from agent_gateway.models import AgentActionAudit
from auth_app.models import RolePermission
from products.models import Product


def agent_client(user, skill='furniture-catalog'):
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Token {token.key}',
        HTTP_X_AGENT_SKILL=skill,
    )
    return client


@pytest.mark.django_db
class TestAgentCatalogTools:
    def test_search_returns_compact_products_and_deep_links(
        self,
        admin_user,
        product_matrix,
        product_rule,
        settings,
    ):
        settings.PUBLIC_WEB_URL = 'https://furniture.example.com'
        client = agent_client(admin_user)

        response = client.get('/api/agent/products/search/', {
            'q': 'M-Chair',
            'category_l1': 'SEATING',
            'origin': 'IMPORT',
            'page_size': 5,
        })

        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['items'][0]['id'] == product_matrix.id
        assert response.data['items'][0]['web_url'] == (
            f'https://furniture.example.com/products/{product_matrix.id}'
        )
        assert 'description' not in response.data['items'][0]

    def test_detail_hides_inactive_product_from_staff(
        self,
        staff_user,
        product_matrix,
    ):
        product_matrix.is_active = False
        product_matrix.save(update_fields=['is_active'])
        client = agent_client(staff_user)

        response = client.get(f'/api/agent/products/{product_matrix.id}/')

        assert response.status_code == 404

    def test_price_is_calculated_by_domain_service(self, admin_user, product_matrix):
        client = agent_client(admin_user, 'furniture-product-config')

        response = client.post(
            f'/api/agent/products/{product_matrix.id}/price/',
            {'selections': {'color': 'red', 'size': 'L'}},
            format='json',
        )

        assert response.status_code == 200
        assert response.data['valid'] is True
        assert Decimal(str(response.data['price'])) == Decimal('2580')
        assert response.data['source'] == 'PriceCalculationService'

    def test_missing_catalog_permission_is_denied_and_audited(
        self,
        staff_user,
        product_matrix,
    ):
        RolePermission.objects.create(
            role='STAFF', module='CATALOG', action='view', allowed=False,
        )
        client = agent_client(staff_user)

        response = client.get('/api/agent/products/search/', {'q': product_matrix.name})

        assert response.status_code == 403
        audit = AgentActionAudit.objects.get(action='catalog.search')
        assert audit.status == AgentActionAudit.Status.DENIED


@pytest.mark.django_db
class TestCapabilityVisibility:
    def test_capabilities_only_include_allowed_domain_tools(self, staff_user):
        RolePermission.objects.bulk_create([
            RolePermission(role='STAFF', module='CATALOG', action='view', allowed=True),
            RolePermission(role='STAFF', module='PRODUCT', action='view', allowed=False),
            RolePermission(role='STAFF', module='DOCUMENT', action='view', allowed=False),
            RolePermission(role='STAFF', module='CASE', action='view', allowed=False),
        ])
        client = agent_client(staff_user, 'furniture-system')

        response = client.get('/api/agent/capabilities/')

        names = {item['name'] for item in response.data['capabilities']}
        assert 'product_search' in names
        assert 'product_detail' not in names
        assert 'document_search' not in names
        assert 'case_search' not in names
