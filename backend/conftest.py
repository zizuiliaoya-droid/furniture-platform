"""Pytest 全局 fixture（测试用 SQLite in-memory）。"""
import os

# 强制测试用 SQLite，避免依赖 PostgreSQL
os.environ.setdefault('DB_ENGINE', 'sqlite')

import pytest
from decimal import Decimal


@pytest.fixture
def admin_user(db):
    from auth_app.models import User
    return User.objects.create_user(
        username='admin', password='admin123456',
        role='ADMIN', display_name='管理员', is_staff=True, is_superuser=True,
    )


@pytest.fixture
def staff_user(db):
    from auth_app.models import User
    return User.objects.create_user(
        username='staff', password='staff123456',
        role='STAFF', display_name='员工',
    )


@pytest.fixture
def brand(db):
    from products.models import Brand
    return Brand.objects.create(name='ZIKOO', is_self_owned=True, sort_order=1)


@pytest.fixture
def product_matrix(db, admin_user, brand):
    """MATRIX 模式产品（含两个维度 + 一个映射）"""
    from products.models import Product, ProductConfigDimension, ProductPriceMatrix
    p = Product.objects.create(
        name='M-Chair', code='MC-001', category_l1='SEATING',
        category_l2='TASK_CHAIR', brand=brand, origin='IMPORT',
        pricing_mode='MATRIX', created_by=admin_user, is_active=True,
    )
    ProductConfigDimension.objects.create(
        product=p, dimension_key='color', dimension_label='颜色',
        options=[{'key': 'red', 'label': 'red'}, {'key': 'blue', 'label': 'blue'}],
        is_required=True, sort_order=1,
    )
    ProductConfigDimension.objects.create(
        product=p, dimension_key='size', dimension_label='尺寸',
        options=[{'key': 'S', 'label': 'S'}, {'key': 'L', 'label': 'L'}],
        is_required=True, sort_order=2,
    )
    sig = ProductPriceMatrix.build_signature({'color': 'red', 'size': 'L'})
    ProductPriceMatrix.objects.create(
        product=p, config_signature=sig,
        config_attributes={'color': 'red', 'size': 'L'},
        price=Decimal('2580'),
    )
    return p


@pytest.fixture
def product_rule(db, admin_user, brand):
    """RULE 模式产品（基准价 + delta 规则）"""
    from products.models import Product, ProductConfigDimension, ProductPriceRule
    p = Product.objects.create(
        name='R-Chair', code='RC-001', category_l1='SEATING',
        category_l2='TASK_CHAIR', brand=brand, origin='DOMESTIC',
        pricing_mode='RULE', base_price=Decimal('1000'),
        created_by=admin_user, is_active=True,
    )
    ProductConfigDimension.objects.create(
        product=p, dimension_key='material', dimension_label='材质',
        options=[{'key': 'mesh', 'label': 'mesh'}, {'key': 'leather', 'label': 'leather'}],
        is_required=True, sort_order=1,
    )
    ProductConfigDimension.objects.create(
        product=p, dimension_key='armrest', dimension_label='扶手',
        options=[{'key': '2D', 'label': '2D'}, {'key': '4D', 'label': '4D'}],
        is_required=False, sort_order=2,
    )
    ProductPriceRule.objects.create(
        product=p, dimension_key='material', option_key='leather',
        price_delta=Decimal('500'),
    )
    ProductPriceRule.objects.create(
        product=p, dimension_key='armrest', option_key='4D',
        price_delta=Decimal('200'),
    )
    return p


@pytest.fixture
def product_cascade(db, admin_user, brand):
    """带级联约束的产品"""
    from products.models import Product, ProductConfigDimension, ProductPriceMatrix
    p = Product.objects.create(
        name='C-Chair', code='CC-001', category_l1='SEATING',
        category_l2='TASK_CHAIR', brand=brand, origin='IMPORT',
        pricing_mode='MATRIX', created_by=admin_user, is_active=True,
    )
    ProductConfigDimension.objects.create(
        product=p, dimension_key='backrest_material', dimension_label='靠背材质',
        options=[{'key': 'mesh', 'label': 'mesh'}, {'key': 'leather', 'label': 'leather'}],
        is_required=True, sort_order=1,
    )
    ProductConfigDimension.objects.create(
        product=p, dimension_key='backrest_series', dimension_label='靠背系列',
        options=[{'key': 'AIR', 'label': 'AIR'}, {'key': '3D', 'label': '3D'}],
        parent_dimension='backrest_material=mesh',
        is_required=False, sort_order=2,
    )
    sig = ProductPriceMatrix.build_signature({'backrest_material': 'mesh', 'backrest_series': 'AIR'})
    ProductPriceMatrix.objects.create(
        product=p, config_signature=sig,
        config_attributes={'backrest_material': 'mesh', 'backrest_series': 'AIR'},
        price=Decimal('3000'),
    )
    return p


@pytest.fixture
def quote(db, admin_user):
    from quotes.models import Quote
    return Quote.objects.create(
        title='测试报价单', customer_name='测试客户',
        status='DRAFT', created_by=admin_user,
    )


@pytest.fixture
def product_image(db, product_matrix):
    """属于 product_matrix 的图片"""
    from products.models import ProductImage
    return ProductImage.objects.create(
        product=product_matrix, image_path='products/test.jpg',
        thumbnail_path={}, sort_order=0, is_cover=True,
    )


@pytest.fixture
def other_product_image(db, product_rule):
    """属于另一个产品（product_rule）的图片，用于校验归属"""
    from products.models import ProductImage
    return ProductImage.objects.create(
        product=product_rule, image_path='products/other.jpg',
        thumbnail_path={}, sort_order=0,
    )
