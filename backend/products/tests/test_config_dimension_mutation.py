"""安全配置维度变更回归测试。"""
from decimal import Decimal

import pytest

from products.models import (
    ProductConfigDimension,
    ProductConfigPreset,
    ProductPriceMatrix,
)
from products.services import DimensionMutationService
from quotes.models import Quote, QuoteItem


@pytest.mark.django_db
class TestDimensionMutationService:
    def test_referenced_dimension_key_and_option_are_locked(self, product_matrix):
        color = product_matrix.config_dimensions.get(dimension_key='color')

        impact = DimensionMutationService.impact(color)

        assert impact['key_locked'] is True
        assert impact['locked_option_keys'] == ['red']
        with pytest.raises(ValueError, match='不能直接修改维度键'):
            DimensionMutationService.update(
                product_matrix,
                color.id,
                {'dimension_key': 'finish', 'options': color.options},
            )
        with pytest.raises(ValueError, match='red'):
            DimensionMutationService.update(
                product_matrix,
                color.id,
                {'options': [{'key': 'blue', 'label': '蓝色'}]},
            )

    def test_cycle_is_rejected_without_changing_dimension(self, product_cascade):
        parent = product_cascade.config_dimensions.get(
            dimension_key='backrest_material',
        )

        with pytest.raises(ValueError, match='循环依赖'):
            DimensionMutationService.update(
                product_cascade,
                parent.id,
                {
                    'options': parent.options,
                    'parent_dimension': 'backrest_series=AIR',
                },
            )

        parent.refresh_from_db()
        assert parent.parent_dimension == ''

    def test_child_dimension_blocks_force_delete(self, product_cascade):
        parent = product_cascade.config_dimensions.get(
            dimension_key='backrest_material',
        )

        with pytest.raises(ValueError, match='下级维度'):
            DimensionMutationService.delete(
                product_cascade,
                parent.id,
                force=True,
            )

        assert ProductConfigDimension.objects.filter(pk=parent.id).exists()

    def test_force_delete_removes_live_pricing_but_preserves_quote_snapshot(
        self,
        product_matrix,
        admin_user,
    ):
        color = product_matrix.config_dimensions.get(dimension_key='color')
        ProductConfigPreset.objects.create(
            product=product_matrix,
            code='RED-L',
            selections={'color': 'red', 'size': 'L'},
            is_default=True,
        )
        quote = Quote.objects.create(
            title='历史报价',
            customer_name='客户',
            created_by=admin_user,
        )
        item = QuoteItem.objects.create(
            quote=quote,
            product=product_matrix,
            product_name=product_matrix.name,
            config_name='红色 / L',
            config_attributes={'color': 'red', 'size': 'L'},
            unit_price=Decimal('2580'),
            quantity=1,
        )

        result = DimensionMutationService.delete(
            product_matrix,
            color.id,
            force=True,
        )

        assert result['removed']['matrix_rows'] >= 1
        assert not ProductPriceMatrix.objects.filter(product=product_matrix).exists()
        assert not ProductConfigPreset.objects.filter(product=product_matrix).exists()
        item.refresh_from_db()
        assert item.config_attributes == {'color': 'red', 'size': 'L'}
        assert item.unit_price == Decimal('2580')
        product_matrix.refresh_from_db()
        assert product_matrix.min_price is None
