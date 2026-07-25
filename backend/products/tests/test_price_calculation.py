"""PriceCalculationService 单元测试。"""
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from auth_app.models import RolePermission
from products.services import PriceCalculationService


@pytest.mark.django_db
class TestMatrixMode:
    def test_matrix_hit(self, product_matrix):
        result = PriceCalculationService.calculate(
            product_matrix, {'color': 'red', 'size': 'L'},
        )
        assert result['valid'] is True
        assert result['price'] == Decimal('2580')
        assert result['missing_dimensions'] == []
        assert result['invalid_selections'] == []

    def test_matrix_miss(self, product_matrix):
        result = PriceCalculationService.calculate(
            product_matrix, {'color': 'blue', 'size': 'S'},
        )
        assert result['valid'] is False
        assert result['price'] is None
        assert '无对应价格' in result['reason']


@pytest.mark.django_db
class TestRuleMode:
    def test_rule_accumulate(self, product_rule):
        # 1000 + 500(leather) + 200(4D) = 1700
        result = PriceCalculationService.calculate(
            product_rule, {'material': 'leather', 'armrest': '4D'},
        )
        assert result['valid'] is True
        assert result['price'] == Decimal('1700')
        deltas = result['breakdown']['deltas']
        assert len(deltas) == 2

    def test_rule_with_no_matching_delta(self, product_rule):
        # mesh 没有规则 → delta=0；只有 base_price=1000
        result = PriceCalculationService.calculate(
            product_rule, {'material': 'mesh'},
        )
        assert result['valid'] is True
        assert result['price'] == Decimal('1000')


@pytest.mark.django_db
class TestValidation:
    def test_missing_required(self, product_matrix):
        # 只选了 color，缺 size
        result = PriceCalculationService.calculate(
            product_matrix, {'color': 'red'},
        )
        assert result['valid'] is False
        assert 'size' in result['missing_dimensions']

    def test_invalid_option_key(self, product_matrix):
        # color=green 不在选项里
        result = PriceCalculationService.calculate(
            product_matrix, {'color': 'green', 'size': 'L'},
        )
        assert result['valid'] is False
        assert any(
            iv['dimension_key'] == 'color' and iv['option_key'] == 'green'
            for iv in result['invalid_selections']
        )

    def test_invalid_dimension_key(self, product_matrix):
        # 维度 'unknown' 不属于该产品
        result = PriceCalculationService.calculate(
            product_matrix, {'color': 'red', 'size': 'L', 'unknown': 'x'},
        )
        assert result['valid'] is False
        assert any(iv['dimension_key'] == 'unknown' for iv in result['invalid_selections'])


@pytest.mark.django_db
class TestCascadeConstraint:
    def test_cascade_parent_unselected(self, product_cascade):
        # 选了子维度 backrest_series=AIR，但未选父维度 backrest_material
        result = PriceCalculationService.calculate(
            product_cascade, {'backrest_series': 'AIR'},
        )
        # 父维度 backrest_material 是 required，因此先以 missing_dimensions 报错
        assert result['valid'] is False
        assert 'backrest_material' in result['missing_dimensions']

    def test_cascade_parent_value_mismatch(self, product_cascade):
        # backrest_material=leather 但 backrest_series 仅在 mesh 时可选
        result = PriceCalculationService.calculate(
            product_cascade,
            {'backrest_material': 'leather', 'backrest_series': 'AIR'},
        )
        assert result['valid'] is False
        assert result['reason'] == '级联约束不满足'
        assert any(
            iv['dimension_key'] == 'backrest_series'
            for iv in result['invalid_selections']
        )

    def test_cascade_satisfied(self, product_cascade):
        # backrest_material=mesh + backrest_series=AIR 满足级联，命中映射价格
        result = PriceCalculationService.calculate(
            product_cascade,
            {'backrest_material': 'mesh', 'backrest_series': 'AIR'},
        )
        assert result['valid'] is True
        assert result['price'] == Decimal('3000')


@pytest.mark.django_db
class TestConditionalRequiredAndFixedPrice:
    def test_invisible_required_child_is_not_missing(self, product_cascade):
        from products.models import ProductPriceMatrix

        child = product_cascade.config_dimensions.get(dimension_key='backrest_series')
        child.is_required = True
        child.save(update_fields=['is_required'])
        config = {'backrest_material': 'leather'}
        ProductPriceMatrix.objects.create(
            product=product_cascade,
            config_signature=ProductPriceMatrix.build_signature(config),
            config_attributes=config,
            price=Decimal('2800'),
        )
        result = PriceCalculationService.calculate(product_cascade, config)
        assert result['valid'] is True
        assert result['price'] == Decimal('2800')

    def test_product_without_dimensions_uses_fixed_price(self, admin_user):
        from products.models import Product

        product = Product.objects.create(
            name='固定价产品', code='FIXED-01', category_l1='ACCESSORIES',
            origin='DOMESTIC', pricing_mode='MATRIX', base_price=Decimal('999'),
            created_by=admin_user, is_active=True,
        )
        result = PriceCalculationService.calculate(product, {})
        assert result['valid'] is True
        assert result['price'] == Decimal('999')


@pytest.mark.django_db
class TestCalculatePricePermission:
    def test_view_permission_is_sufficient_for_post_calculation(self, staff_user, product_matrix):
        RolePermission.objects.create(
            role='STAFF', module='PRODUCT', action='view', allowed=True)
        client = APIClient()
        client.force_authenticate(staff_user)
        response = client.post(
            f'/api/products/{product_matrix.id}/calculate-price/',
            {'selections': {'color': 'red', 'size': 'L'}}, format='json')
        assert response.status_code == 200, response.content
        assert response.data['price'] == '2580.00'

    def test_create_without_view_cannot_calculate(self, staff_user, product_matrix):
        RolePermission.objects.create(
            role='STAFF', module='PRODUCT', action='create', allowed=True)
        client = APIClient()
        client.force_authenticate(staff_user)
        response = client.post(
            f'/api/products/{product_matrix.id}/calculate-price/',
            {'selections': {'color': 'red', 'size': 'L'}}, format='json')
        assert response.status_code == 403