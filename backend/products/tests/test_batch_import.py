"""批量产品导入（长格式）回归测试。"""
from io import BytesIO

import pytest

from products.models import Product, ProductConfigDimension, ProductConfigPreset
from products.services import BatchProductImportService


@pytest.mark.django_db
class TestBatchImport:
    def test_template_roundtrip(self, admin_user):
        # 用模板本身作为导入源，验证解析 + 入库闭环
        template = BatchProductImportService.generate_template()
        parsed = BatchProductImportService.parse(BytesIO(template))
        assert parsed['summary']['product_count'] == 1
        assert not parsed['errors']

        result = BatchProductImportService.execute_import(parsed, admin_user)
        assert result['created'] == 1

        p = Product.objects.get(code='ZK-LEADER-01')
        assert p.category_l1 == 'DESKS_WORKSTATIONS'
        assert p.shape == '方形'
        # 桌板材质 + 产品规格 两个维度
        dims = ProductConfigDimension.objects.filter(product=p)
        assert dims.count() == 2
        keys = set(dims.values_list('dimension_key', flat=True))
        assert '桌板材质' in keys and '产品规格' in keys
        # 旧“配置款式”不包含完整 selections，不再生成空默认预设。
        presets = ProductConfigPreset.objects.filter(product=p)
        assert presets.count() == 0

    def test_idempotent_update(self, admin_user):
        template = BatchProductImportService.generate_template()
        BatchProductImportService.execute_import(
            BatchProductImportService.parse(BytesIO(template)), admin_user)
        # 再次导入应更新而非重复
        result = BatchProductImportService.execute_import(
            BatchProductImportService.parse(BytesIO(template)), admin_user)
        assert result['updated'] == 1
        assert Product.objects.filter(code='ZK-LEADER-01').count() == 1
