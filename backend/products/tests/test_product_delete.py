"""产品删除回归测试：默认软删除（下架），?hard=true 永久删除。"""
import pytest
from rest_framework.test import APIClient

from products.models import Product


@pytest.fixture
def api(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.mark.django_db
class TestProductDelete:
    def test_soft_delete_deactivates(self, api, product_matrix):
        resp = api.delete(f'/api/products/{product_matrix.id}/')
        assert resp.status_code == 204
        product_matrix.refresh_from_db()
        assert product_matrix.is_active is False
        # 记录仍在
        assert Product.objects.filter(id=product_matrix.id).exists()

    def test_hard_delete_removes(self, api, product_matrix):
        pid = product_matrix.id
        resp = api.delete(f'/api/products/{pid}/?hard=true')
        assert resp.status_code == 204
        assert not Product.objects.filter(id=pid).exists()

    def test_staff_cannot_delete(self, staff_user, product_matrix):
        client = APIClient()
        client.force_authenticate(user=staff_user)
        resp = client.delete(f'/api/products/{product_matrix.id}/?hard=true')
        assert resp.status_code in (403, 404)
        assert Product.objects.filter(id=product_matrix.id).exists()
