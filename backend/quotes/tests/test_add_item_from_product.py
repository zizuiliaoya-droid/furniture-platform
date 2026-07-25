"""QuoteService.add_item_from_product 单元测试。"""
from decimal import Decimal
from io import BytesIO

import openpyxl
import pytest
from PIL import Image
from django.test import override_settings
from rest_framework.exceptions import ValidationError

from quotes.services import QuoteExcelService, QuoteService


@pytest.mark.django_db
class TestAddItemFromProduct:
    def test_success(self, quote, product_matrix):
        item = QuoteService.add_item_from_product(
            quote=quote,
            product=product_matrix,
            selections={'color': 'red', 'size': 'L'},
            quantity=2,
        )
        assert item.unit_price == Decimal('2580')
        assert item.quantity == 2
        assert item.discount == Decimal('0')
        assert item.subtotal == Decimal('5160.00')
        assert item.config_attributes == {'color': 'red', 'size': 'L'}
        # 总价被重算，单项折扣始终为 0。
        quote.refresh_from_db()
        assert quote.total_amount == Decimal('5160.00')

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
            quantity=1,
        )
        QuoteService.add_item_from_product(
            quote=quote, product=product_matrix,
            selections={'color': 'red', 'size': 'L'},
            quantity=1,
        )
        quote.refresh_from_db()
        # 2580 + 2580 = 5160
        assert quote.total_amount == Decimal('5160.00')
        assert quote.items.count() == 2

    def test_uses_cover_and_chinese_summary_by_default(self, quote, product_matrix, product_image):
        item = QuoteService.add_item_from_product(
            quote=quote, product=product_matrix,
            selections={'color': 'red', 'size': 'L'},
        )
        assert item.image_id == product_image.id
        assert item.config_name == '颜色:red / 尺寸:L'

    def test_fixed_price_product_without_dimensions(self, quote, admin_user):
        from products.models import Product

        product = Product.objects.create(
            name='固定价边几', code='FIXED-TABLE', category_l1='DESKS_WORKSTATIONS',
            origin='DOMESTIC', pricing_mode='MATRIX', base_price=Decimal('880'),
            created_by=admin_user, is_active=True,
        )
        item = QuoteService.add_item_from_product(quote, product, {})
        assert item.unit_price == Decimal('880')
        assert item.config_attributes == {}


@pytest.mark.django_db
class TestQuoteExcelImage:
    def test_quotation_excel_embeds_product_image(
        self, tmp_path, quote, product_matrix, product_image,
    ):
        image_dir = tmp_path / 'products'
        image_dir.mkdir()
        Image.new('RGB', (20, 20), color='red').save(image_dir / 'test.jpg')
        QuoteService.add_item_from_product(
            quote=quote, product=product_matrix,
            selections={'color': 'red', 'size': 'L'},
        )
        with override_settings(MEDIA_ROOT=tmp_path):
            content = QuoteExcelService.export_quotation(quote)
        workbook = openpyxl.load_workbook(BytesIO(content))
        assert len(workbook['报价单']._images) == 1
