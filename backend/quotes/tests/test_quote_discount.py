"""QT-6：整单折扣改造回归测试。"""
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from quotes.models import QuoteItem


@pytest.fixture
def api(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.mark.django_db
class TestQuoteDiscount:
    def test_whole_quote_discount_applies(self, api, quote, product_matrix):
        # 加两条明细：2580 * 2 = 5160
        for _ in range(2):
            QuoteItem.objects.create(
                quote=quote, product=product_matrix, product_name=product_matrix.name,
                unit_price=Decimal('2580'), quantity=1, discount=Decimal('0'),
            )
        quote.recalculate_total()
        assert quote.total_amount == Decimal('5160.00')

        # 设置整单 10% 折扣 → 5160 * 0.9 = 4644
        resp = api.patch(f'/api/quotes/{quote.id}/', {'discount': '10'}, format='json')
        assert resp.status_code == 200, resp.content
        quote.refresh_from_db()
        assert quote.total_amount == Decimal('4644.00')

    def test_zero_discount_equals_subtotal(self, api, quote, product_matrix):
        QuoteItem.objects.create(
            quote=quote, product=product_matrix, product_name=product_matrix.name,
            unit_price=Decimal('1000'), quantity=3, discount=Decimal('0'),
        )
        quote.recalculate_total()
        assert quote.total_amount == Decimal('3000.00')
