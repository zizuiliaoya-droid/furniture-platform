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
    def test_patch_quantity_and_discount(self, api, quote, quote_item):
        resp = api.patch(
            f'/api/quotes/items/{quote_item.id}/',
            {'quantity': 3, 'discount': '10'}, format='json',
        )
        assert resp.status_code == 200, resp.content
        quote_item.refresh_from_db()
        assert quote_item.quantity == 3
        assert quote_item.discount == Decimal('10')
        # 2580 * 3 * 0.9 = 6966
        assert quote_item.subtotal == Decimal('6966.00')
        quote.refresh_from_db()
        assert quote.total_amount == Decimal('6966.00')

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
