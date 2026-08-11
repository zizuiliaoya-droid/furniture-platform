"""通用配置 Excel 解析、预览和事务化导入回归测试。"""
from io import BytesIO

import openpyxl
import pytest

from products.models import ProductConfigPreset, ProductPriceMatrix
from products.services import FlexibleConfigExcelService


def workbook_bytes(sheets):
    workbook = openpyxl.Workbook()
    first = True
    for name, rows in sheets:
        worksheet = workbook.active if first else workbook.create_sheet()
        first = False
        worksheet.title = name
        for row in rows:
            worksheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


@pytest.mark.django_db
class TestFlexibleConfigExcelService:
    def test_detects_custom_combination_and_preview_does_not_mutate(self, product_matrix):
        source = workbook_bytes([
            ('产品配置', [
                ['组合编号', '颜色', '尺寸', '最终价格', '是否默认'],
                ['RED-L', '红', 'L', 2680, '是'],
                ['BLUE-S', '蓝', 'S', 2380, '否'],
            ]),
        ])
        before = {
            'dimensions': product_matrix.config_dimensions.count(),
            'prices': product_matrix.price_matrix.count(),
        }

        parsed = FlexibleConfigExcelService.parse_excel(product_matrix, source)

        assert parsed['detected_format'] == 'combination'
        assert parsed['needs_mapping'] is False
        assert parsed['errors'] == []
        assert parsed['success_count'] == 2
        assert [item['dimension_label'] for item in parsed['dimensions']] == ['颜色', '尺寸']
        assert product_matrix.config_dimensions.count() == before['dimensions']
        assert product_matrix.price_matrix.count() == before['prices']

    def test_multiple_candidate_sheets_require_explicit_mapping(self, product_matrix):
        source = workbook_bytes([
            ('配置一', [['颜色', '尺寸'], ['红', 'L']]),
            ('配置二', [['材质', '脚架'], ['布', '钢']]),
        ])

        parsed = FlexibleConfigExcelService.parse_excel(product_matrix, source)

        assert parsed['needs_mapping'] is True
        assert parsed['detected_format'] == 'mapping_required'
        assert parsed['available_sheets'][0]['name'] == '配置一'

    def test_standard_dimensions_only_merge_preserves_prices_and_presets(self, product_matrix):
        ProductConfigPreset.objects.create(
            product=product_matrix,
            code='ORIGINAL',
            selections={'color': 'red', 'size': 'L'},
            is_default=True,
        )
        source = workbook_bytes([
            ('dimensions', [
                [
                    'dimension_key', 'dimension_label', 'options',
                    'parent_dimension', 'is_required', 'sort_order',
                ],
                ['color', '颜色（新）', 'red|红,blue|蓝,green|绿', '', 'TRUE', 1],
                ['size', '尺寸', 'S,L', '', 'TRUE', 2],
            ]),
        ])
        parsed = FlexibleConfigExcelService.parse_excel(product_matrix, source)

        result = FlexibleConfigExcelService.execute_import(product_matrix, parsed)

        assert result == {
            'dimensions': 2,
            'prices': 0,
            'presets': 0,
            'mode': 'merge',
        }
        assert ProductPriceMatrix.objects.filter(product=product_matrix).count() == 1
        assert ProductConfigPreset.objects.filter(product=product_matrix).count() == 1
        color = product_matrix.config_dimensions.get(dimension_key='color')
        assert color.dimension_label == '颜色（新）'
        assert color.options[-1] == {'key': 'green', 'label': '绿'}

    def test_replace_without_prices_is_rejected_and_rolls_back(self, product_matrix):
        original_dimension_ids = list(
            product_matrix.config_dimensions.values_list('id', flat=True),
        )
        original_signature = product_matrix.price_matrix.get().config_signature
        source = workbook_bytes([
            ('dimensions', [
                ['dimension_key', 'dimension_label', 'options'],
                ['finish', '饰面', 'oak|橡木,walnut|胡桃木'],
            ]),
        ])
        parsed = FlexibleConfigExcelService.parse_excel(product_matrix, source)

        with pytest.raises(ValueError, match='必须同时提供完整价格数据'):
            FlexibleConfigExcelService.execute_import(
                product_matrix,
                parsed,
                replace_dimensions=True,
            )

        assert list(product_matrix.config_dimensions.values_list('id', flat=True)) == original_dimension_ids
        assert product_matrix.price_matrix.get().config_signature == original_signature

    def test_invalid_empty_workbook_reports_consistent_failure_count(self, product_matrix):
        source = workbook_bytes([('空表', [['无关列'], ['']])])

        parsed = FlexibleConfigExcelService.parse_excel(product_matrix, source)

        assert parsed['errors']
        assert parsed['failed_count'] == len(parsed['errors'])
