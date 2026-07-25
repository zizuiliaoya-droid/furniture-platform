"""产品事务化组合创建回归测试。"""
import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from products.models import Product, ProductConfigDimension
from products.services import ProductImageService


@pytest.fixture
def api(admin_user):
    client = APIClient()
    client.force_authenticate(admin_user)
    return client


def payload(code='COMPOSITE-01'):
    return {
        'product': {
            'name': '事务产品', 'code': code, 'category_l1': 'SEATING',
            'category_l2': 'TASK_CHAIR', 'origin': 'DOMESTIC',
            'pricing_mode': 'MATRIX', 'is_active': True,
        },
        'dimensions': [{
            'dimension_key': 'color', 'dimension_label': '颜色',
            'options': [{'key': 'red', 'label': '红色'}],
            'parent_dimension': '', 'is_required': True, 'sort_order': 0,
        }],
        'presets': [], 'price_matrix': [],
    }


@pytest.mark.django_db
class TestCompositeCreate:
    def test_success_creates_product_and_dimensions(self, api):
        response = api.post('/api/products/create-composite/',
                            {'payload': json.dumps(payload())}, format='multipart')
        assert response.status_code == 201, response.content
        product = Product.objects.get(code='COMPOSITE-01')
        assert ProductConfigDimension.objects.filter(product=product).count() == 1

    def test_duplicate_dimension_rolls_back(self, api):
        data = payload('COMPOSITE-DUP')
        data['dimensions'].append(dict(data['dimensions'][0]))
        response = api.post('/api/products/create-composite/',
                            {'payload': json.dumps(data)}, format='multipart')
        assert response.status_code == 400
        assert not Product.objects.filter(code='COMPOSITE-DUP').exists()

    def test_image_failure_rolls_back_product(self, api, monkeypatch):
        def fail_upload(*_args, **_kwargs):
            raise ValueError('模拟图片写入失败')

        monkeypatch.setattr(ProductImageService, 'upload_images', fail_upload)
        data = payload('COMPOSITE-ROLLBACK')
        response = api.post(
            '/api/products/create-composite/',
            {
                'payload': json.dumps(data),
                'images': [SimpleUploadedFile(
                    'test.jpg', b'fake-image', content_type='image/jpeg')],
            },
            format='multipart',
        )
        assert response.status_code == 400
        assert not Product.objects.filter(code='COMPOSITE-ROLLBACK').exists()

    def test_staff_create_permission_uses_matrix(self, staff_user):
        from auth_app.models import RolePermission

        RolePermission.objects.create(
            role='STAFF', module='PRODUCT', action='create', allowed=True)
        client = APIClient()
        client.force_authenticate(staff_user)
        response = client.post(
            '/api/products/create-composite/',
            {'payload': json.dumps(payload('STAFF-COMPOSITE'))}, format='multipart')
        assert response.status_code == 201, response.content
        assert Product.objects.filter(code='STAFF-COMPOSITE').exists()
