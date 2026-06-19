"""Catalog 筛选 API 单元测试。"""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.mark.django_db
class TestCatalogFilters:
    def test_fixed_brand_filter(self, api_client, product_matrix, product_rule):
        # product_matrix 和 product_rule 共享同一个 brand
        resp = api_client.get('/api/catalog/', {'brand[]': str(product_matrix.brand_id)})
        assert resp.status_code == 200
        data = resp.json()
        results = data.get('results', data)
        names = [p['name'] for p in results]
        assert 'M-Chair' in names
        assert 'R-Chair' in names

    def test_fixed_category_l1_l2(self, api_client, product_matrix):
        resp = api_client.get(
            '/api/catalog/',
            {'category_l1[]': 'SEATING', 'category_l2[]': 'TASK_CHAIR'},
        )
        assert resp.status_code == 200
        results = resp.json().get('results', resp.json())
        assert any(p['name'] == 'M-Chair' for p in results)

    def test_mece_length_range(self, api_client, admin_user, brand):
        # 创建一个尺寸在 600-900 范围内的产品
        from products.models import Product
        Product.objects.create(
            name='InRange', code='IR-001', category_l1='SEATING',
            brand=brand, origin='IMPORT', pricing_mode='MATRIX',
            length_mm=750, created_by=admin_user, is_active=True,
        )
        Product.objects.create(
            name='OutOfRange', code='OOR-001', category_l1='SEATING',
            brand=brand, origin='IMPORT', pricing_mode='MATRIX',
            length_mm=1500, created_by=admin_user, is_active=True,
        )
        resp = api_client.get('/api/catalog/', {'length_range': '600-900'})
        assert resp.status_code == 200
        names = [p['name'] for p in resp.json().get('results', resp.json())]
        assert 'InRange' in names
        assert 'OutOfRange' not in names

    def test_mece_price_range_unbounded(self, api_client, admin_user, brand):
        # price_range='-1000' 表示 ≤1000
        from decimal import Decimal
        from products.models import Product
        Product.objects.create(
            name='Cheap', code='CHP-001', category_l1='SEATING',
            brand=brand, origin='IMPORT', pricing_mode='MATRIX',
            min_price=Decimal('500'), created_by=admin_user, is_active=True,
        )
        Product.objects.create(
            name='Pricey', code='PR-001', category_l1='SEATING',
            brand=brand, origin='IMPORT', pricing_mode='MATRIX',
            min_price=Decimal('5000'), created_by=admin_user, is_active=True,
        )
        resp = api_client.get('/api/catalog/', {'price_range': '-1000'})
        assert resp.status_code == 200
        names = [p['name'] for p in resp.json().get('results', resp.json())]
        assert 'Cheap' in names
        assert 'Pricey' not in names

    def test_dynamic_attribute_filter(self, api_client, product_matrix):
        # product_matrix 含 dimension color 选项 red/blue
        resp = api_client.get('/api/catalog/', {'attr_color[]': 'red'})
        assert resp.status_code == 200
        names = [p['name'] for p in resp.json().get('results', resp.json())]
        assert 'M-Chair' in names

    def test_combined_filters(self, api_client, product_matrix):
        resp = api_client.get('/api/catalog/', {
            'brand[]': str(product_matrix.brand_id),
            'category_l1[]': 'SEATING',
            'origin[]': 'IMPORT',
        })
        assert resp.status_code == 200
        names = [p['name'] for p in resp.json().get('results', resp.json())]
        assert 'M-Chair' in names
