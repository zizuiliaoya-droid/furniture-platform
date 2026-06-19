"""Quote services."""
import os
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError

try:
    from weasyprint import HTML
    HAS_WEASYPRINT = True
except (ImportError, OSError):
    HAS_WEASYPRINT = False

from .models import Quote, QuoteItem

VALID_TRANSITIONS = {
    'DRAFT': ['SENT', 'CANCELLED'],
    'SENT': ['CONFIRMED', 'CANCELLED'],
    'CONFIRMED': ['CANCELLED'],
    'CANCELLED': [],
}


class QuoteService:
    @staticmethod
    def validate_status_change(current: str, new_status: str) -> bool:
        return new_status in VALID_TRANSITIONS.get(current, [])

    @staticmethod
    @transaction.atomic
    def duplicate(quote_id: int, user) -> Quote:
        original = Quote.objects.prefetch_related('items').get(pk=quote_id)
        new_quote = Quote.objects.create(
            title=f"{original.title}(副本)",
            customer_name=original.customer_name,
            status='DRAFT',
            notes=original.notes,
            terms=original.terms,
            created_by=user,
        )
        for item in original.items.all():
            QuoteItem.objects.create(
                quote=new_quote,
                product=item.product,
                product_name=item.product_name,
                config_name=item.config_name,
                config_attributes=item.config_attributes,
                image=item.image,
                image_url=item.image_url,
                unit_price=item.unit_price,
                quantity=item.quantity,
                discount=item.discount,
                sort_order=item.sort_order,
            )
        new_quote.recalculate_total()
        return new_quote

    @staticmethod
    def export_pdf(quote_id: int) -> bytes:
        if not HAS_WEASYPRINT:
            raise ImportError('WeasyPrint is not installed. Install it with: pip install WeasyPrint')
        quote = Quote.objects.prefetch_related('items', 'items__image').get(pk=quote_id)
        media_root = str(settings.MEDIA_ROOT)
        # 把 image_url 解析成模板可直接 src 引用的绝对路径
        items_with_abs_image = []
        for item in quote.items.all():
            abs_path = ''
            if item.image_url:
                candidate = os.path.join(media_root, item.image_url)
                if os.path.exists(candidate):
                    # 用 file:// 让 WeasyPrint 把它当本地资源加载
                    abs_path = 'file:///' + candidate.replace('\\', '/').lstrip('/')
            items_with_abs_image.append({'item': item, 'abs_image': abs_path})
        html_string = render_to_string('quotes/pdf_template.html', {
            'quote': quote,
            'items_with_abs_image': items_with_abs_image,
            'MEDIA_ROOT': media_root,
        })
        # base_url 让相对路径能解析到 MEDIA_ROOT
        pdf = HTML(string=html_string, base_url=media_root).write_pdf()
        return pdf

    @staticmethod
    @transaction.atomic
    def add_item_from_product(quote: Quote, product, selections: dict,
                              image_id=None, quantity=1, discount=Decimal('0')):
        """一键加入报价单：算价 + 写明细 + 重算总价"""
        from products.services import PriceCalculationService
        from products.models import ProductImage

        # 1. 复用价格计算
        result = PriceCalculationService.calculate(product, selections)
        if not result['valid']:
            raise ValidationError({
                'detail': result.get('reason', '配置无效'),
                'missing_dimensions': result.get('missing_dimensions', []),
            })

        # 2. 选定明细图
        image = None
        image_url = ''
        if image_id:
            try:
                image = ProductImage.objects.get(pk=image_id, product=product)
                image_url = image.image_path
            except ProductImage.DoesNotExist:
                pass

        # 3. 生成配置摘要文本
        config_name = QuoteService._summarize_selections(product, selections)

        # 4. 写入明细
        item = QuoteItem.objects.create(
            quote=quote,
            product=product,
            product_name=product.name,
            config_name=config_name,
            config_attributes=selections,
            unit_price=Decimal(str(result['price'])),
            quantity=quantity,
            discount=discount,
            image=image,
            image_url=image_url,
            sort_order=quote.items.count(),
        )

        # 5. 触发总价重算
        quote.recalculate_total()
        return item

    @staticmethod
    def _summarize_selections(product, selections: dict) -> str:
        """生成配置摘要文本"""
        from products.models import ProductConfigDimension
        dims = ProductConfigDimension.objects.filter(product=product)
        dim_labels = {d.dimension_key: d.dimension_label for d in dims}
        parts = []
        for key, value in selections.items():
            label = dim_labels.get(key, key)
            parts.append(f"{label}:{value}")
        return ' / '.join(parts) if parts else ''
