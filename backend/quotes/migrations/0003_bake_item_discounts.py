"""QT-6：取消单项折扣。将历史明细的单项折扣"烘焙"进小计后置 0（保总额不变）。

说明：QuoteItem.subtotal 已包含单项折扣（unit_price*qty*(1-discount/100)）。
用 queryset.update 直接把 discount 置 0（绕过 save，不重算 subtotal），
从而保留既有小计与报价单总额；整单折扣默认 0。
"""
from decimal import Decimal
from django.db import migrations


def bake_item_discounts(apps, schema_editor):
    QuoteItem = apps.get_model('quotes', 'QuoteItem')
    QuoteItem.objects.exclude(discount=Decimal('0')).update(discount=Decimal('0'))


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('quotes', '0002_quote_discount'),
    ]
    operations = [
        migrations.RunPython(bake_item_discounts, noop_reverse),
    ]
