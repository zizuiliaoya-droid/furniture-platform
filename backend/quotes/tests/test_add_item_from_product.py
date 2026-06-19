"""QuoteService.add_item_from_product 单元测试。"""
from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError

from quotes.services import QuoteService


@pytest.mark.django_db
class TestAddItemFromProduct:
    def test_success(self, quote, product_matrix):
        item = QuoteService.add_item_from_product(
            quote=quote,
            product=product_matrix,
            selections={'color': 'red', 'size': 'L'},
            quantity=2,
            discount=Decimal('10'),
        )
        assert item.unit_price == Decimal('2580')
        assert item.quantity == 2
        assert item.discount == Decimal('10')
        # 2580 * 2 * 0.9 = 4644
        assert item.subtotal == Decimal('4644.00')
        assert item.config_attributes == {'color': 'red', 'size': 'L'}
        # 总价被重算
        quote.refresh_from_db()
        assert quote.total_amount == Decimal('4644.00')

    def test_invalid_selections_raises(self, quote, product_matrix):
        # 缺必填维度 size
        with pytest.raises(ValidationError):
            QuoteService.add_item_from_product(
                quote=quote, product=product_matrix,
                selections={'color': 'red'},
            )

    def test_image_not_belong_to_product_silently_ignored(
        self, quote, product_matrix, other_product_image,
    ):
        # other_product_image 属于 product_rule，不属于 product_matrix
        item = QuoteService.add_item_from_product(
            quote=quote,
            product=product_matrix,
            selections={'color': 'red', 'size': 'L'},
            image_id=other_product_image.id,
        )
        # 应当忽略不归属的图片，不抛错也不绑定
        assert item.image is None
        assert item.image_url == ''

    def test_image_belongs_to_product(self, quote, product_matrix, product_image):
        item = QuoteService.add_item_from_product(
            quote=quote,
            product=product_matrix,
            selections={'color': 'red', 'size': 'L'},
            image_id=product_image.id,
        )
        assert item.image_id == product_image.id
        assert item.image_url == 'products/test.jpg'

    def test_duplicate_calls_increment_total(self, quote, product_matrix):
        QuoteService.add_item_from_product(
            quote=quote, product=product_matrix,
            selections={'color': 'red', 'size': 'L'},
            quantity=1, discount=Decimal('0'),
        )
        QuoteService.add_item_from_product(
            quote=quote, product=product_matrix,
            selections={'color': 'red', 'size': 'L'},
            quantity=1, discount=Decimal('0'),
        )
        quote.refresh_from_db()
        # 2580 + 2580 = 5160
        assert quote.total_amount == Decimal('5160.00')
        assert quote.items.count() == 2
