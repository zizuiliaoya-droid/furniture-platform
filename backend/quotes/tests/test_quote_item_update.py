"""报价明细更新接口回归测试（修复 #4：编辑明细无法保存）。

复现并验证：PATCH /api/quotes/items/{id}/ 部分更新数量/折扣后
- 能成功保存（此前因 get_queryset 过滤 quote_pk=None + PUT 全量校验而失败）
- subtotal 与报价单 total_amount 同步重算
"""
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from quotes.models import QuoteItem


@pytest.fixture
def api(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def quote_item(db, quote, product_matrix):
    item = QuoteItem.objects.create(
        quote=quote, product=product_matrix, product_name='M-Chair',
        config_name='red / L', unit_price=Decimal('2580'),
        quantity=1, discount=Decimal('0'), sort_order=0,
    )
    quote.recalculate_total()
    return item


@pytest.mark.django_db
class TestQuoteItemUpdate:
    def test_patch_quantity_ignores_legacy_item_discount(self, api, quote, quote_item):
        resp = api.patch(
            f'/api/quotes/items/{quote_item.id}/',
            {'quantity': 3, 'discount': '10'}, format='json',
        )
        assert resp.status_code == 200, resp.content
        quote_item.refresh_from_db()
        assert quote_item.quantity == 3
        assert quote_item.discount == Decimal('0')
        assert quote_item.subtotal == Decimal('7740.00')
        quote.refresh_from_db()
        assert quote.total_amount == Decimal('7740.00')

    def test_patch_only_quantity(self, api, quote_item):
        resp = api.patch(
            f'/api/quotes/items/{quote_item.id}/',
            {'quantity': 5}, format='json',
        )
        assert resp.status_code == 200, resp.content
        quote_item.refresh_from_db()
        assert quote_item.quantity == 5
        # 折扣保持 0：2580 * 5 = 12900
        assert quote_item.subtotal == Decimal('12900.00')

    def test_delete_item_recalculates_total(self, api, quote, quote_item):
        resp = api.delete(f'/api/quotes/items/{quote_item.id}/')
        assert resp.status_code == 204
        quote.refresh_from_db()
        assert quote.total_amount == Decimal('0')
        assert quote.items.count() == 0


@pytest.mark.django_db
class TestUpdateItemFromProduct:
    def test_updates_same_row_and_preserves_quantity(self, api, quote, quote_item, product_matrix, product_image):
        from products.models import ProductPriceMatrix

        quote_item.image = product_image
        quote_item.image_url = product_image.image_path
        quote_item.quantity = 3
        quote_item.save()
        config = {'color': 'blue', 'size': 'S'}
        ProductPriceMatrix.objects.create(
            product=product_matrix,
            config_signature=ProductPriceMatrix.build_signature(config),
            config_attributes=config,
            price=Decimal('2380'),
        )
        count_before = quote.items.count()
        response = api.patch(
            f'/api/quotes/items/{quote_item.id}/from-product/',
            {'product_id': product_matrix.id, 'selections': config}, format='json')
        assert response.status_code == 200, response.content
        quote_item.refresh_from_db()
        assert quote.items.count() == count_before
        assert quote_item.id == response.data['id']
        assert quote_item.quantity == 3
        assert quote_item.image_id == product_image.id
        assert quote_item.unit_price == Decimal('2380')
        assert quote_item.config_name == '颜色:blue / 尺寸:S'

    def test_non_draft_quote_rejects_item_update(self, api, quote, quote_item, product_matrix):
        quote.status = 'SENT'
        quote.save(update_fields=['status'])
        response = api.patch(
            f'/api/quotes/items/{quote_item.id}/from-product/',
            {'product_id': product_matrix.id,
             'selections': {'color': 'red', 'size': 'L'}}, format='json')
        assert response.status_code == 400

    def test_shared_user_cannot_update(self, staff_user, quote, quote_item, product_matrix):
        from auth_app.models import RolePermission
        from quotes.models import QuoteShare

        RolePermission.objects.create(role='STAFF', module='QUOTE', action='update', allowed=True)
        QuoteShare.objects.create(quote=quote, shared_with=staff_user, created_by=quote.created_by)
        client = APIClient()
        client.force_authenticate(staff_user)
        response = client.patch(
            f'/api/quotes/items/{quote_item.id}/from-product/',
            {'product_id': product_matrix.id,
             'selections': {'color': 'red', 'size': 'L'}}, format='json')
        assert response.status_code == 403


@pytest.mark.django_db
class TestQuoteShareCandidates:
    def test_owner_with_share_permission_can_list_candidates(self, staff_user, admin_user):
        from auth_app.models import RolePermission
        from quotes.models import Quote

        RolePermission.objects.create(role='STAFF', module='QUOTE', action='share', allowed=True)
        quote = Quote.objects.create(
            title='员工报价', customer_name='客户', status='DRAFT', created_by=staff_user)
        client = APIClient()
        client.force_authenticate(staff_user)
        response = client.get(f'/api/quotes/{quote.id}/share-candidates/')
        assert response.status_code == 200, response.content
        assert any(user['id'] == admin_user.id for user in response.data)
        assert all(user['id'] != staff_user.id for user in response.data)
