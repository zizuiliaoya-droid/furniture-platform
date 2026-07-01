"""Product management services."""
import hashlib
import json
from decimal import Decimal
from io import BytesIO

import openpyxl
from django.conf import settings
from django.db import transaction

from common.file_storage import FileStorageService
from .models import (
    Brand, Category, Product, ProductConfig, ProductConfigDimension,
    ProductConfigPreset, ProductImage, ProductPriceMatrix, ProductPriceRule,
)


class CategoryService:
    @staticmethod
    def get_tree(dimension: str):
        return Category.objects.filter(
            dimension=dimension, parent__isnull=True
        ).order_by('sort_order', 'id')

    @staticmethod
    def reorder(items: list):
        for item in items:
            Category.objects.filter(pk=item['id']).update(sort_order=item['sort_order'])


class ProductImageService:
    @staticmethod
    def upload_images(product: Product, files: list) -> list:
        created = []
        for f in files:
            if f.size > settings.MAX_IMAGE_SIZE:
                continue
            path = FileStorageService.upload(f, 'products')
            thumbs = FileStorageService.generate_thumbnails(path)
            img = ProductImage.objects.create(
                product=product,
                image_path=path,
                thumbnail_path=thumbs,
                sort_order=product.images.count(),
            )
            created.append(img)
        return created

    @staticmethod
    def delete_image(image: ProductImage):
        FileStorageService.delete_with_thumbnails(image.image_path)
        image.delete()

    @staticmethod
    def set_cover(image: ProductImage):
        ProductImage.objects.filter(product=image.product, is_cover=True).update(is_cover=False)
        image.is_cover = True
        image.save(update_fields=['is_cover'])


class ProductImportService:
    """产品批量导入（旧 Excel 导入，保留兼容）"""
    REQUIRED_HEADERS = ['名称', '产地']
    ORIGIN_MAP = {'进口': 'IMPORT', '国产': 'DOMESTIC'}

    @staticmethod
    def parse_excel(file) -> dict:
        wb = openpyxl.load_workbook(file, read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(min_row=1, values_only=True))
        if not rows:
            return {'success_count': 0, 'failed_count': 0, 'preview': []}
        headers = [str(h).strip() if h else '' for h in rows[0]]
        results = []
        seen_codes = set()
        for i, row in enumerate(rows[1:], start=2):
            data = dict(zip(headers, row))
            errors = []
            name = str(data.get('名称', '') or '').strip()
            if not name:
                errors.append('名称为必填项')
            origin_raw = str(data.get('产地', '') or '').strip()
            origin = ProductImportService.ORIGIN_MAP.get(origin_raw)
            if not origin:
                errors.append(f'产地无效: {origin_raw}')
            code = str(data.get('编号', '') or '').strip() or None
            if code:
                if code in seen_codes or Product.objects.filter(code=code).exists():
                    errors.append(f'编号重复: {code}')
                seen_codes.add(code)
            results.append({
                'row': i, 'name': name, 'code': code, 'origin': origin,
                'description': str(data.get('描述', '') or ''),
                'min_price': data.get('最低售价'),
                'errors': errors,
            })
        success = [r for r in results if not r['errors']]
        failed = [r for r in results if r['errors']]
        return {'success_count': len(success), 'failed_count': len(failed), 'preview': results, 'parsed_data': success}

    @staticmethod
    @transaction.atomic
    def execute_import(parsed_data: list, user) -> int:
        count = 0
        for item in parsed_data:
            Product.objects.create(
                name=item['name'], code=item['code'], origin=item['origin'],
                description=item['description'],
                min_price=item['min_price'] if item['min_price'] else None,
                created_by=user,
            )
            count += 1
        return count

    @staticmethod
    def generate_template():
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = '产品导入模板'
        ws.append(['名称', '编号', '产地', '描述', '最低售价'])
        ws.append(['示例产品', 'P001', '进口', '产品描述', 1000])
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.getvalue()


# ─── 价格计算服务 ─────────────────────────────────────────────────────────────

class PriceCalculationService:
    """产品配置实时计算指导价"""

    @staticmethod
    def _option_keys(dim: 'ProductConfigDimension') -> list:
        """提取一个维度允许的所有 option key"""
        keys = []
        for opt in dim.options or []:
            if isinstance(opt, dict):
                keys.append(opt.get('key', ''))
            else:
                keys.append(str(opt))
        return [k for k in keys if k]

    @staticmethod
    def calculate(product: Product, selections: dict) -> dict:
        """
        入参: product, selections = {dimension_key: option_key, ...}
        返回: {
            valid: bool,
            price: Decimal|None,
            breakdown: dict,
            missing_dimensions: list,
            invalid_selections: list,  # 选项归属/级联非法
            reason: str,
        }
        """
        all_dims = list(ProductConfigDimension.objects.filter(product=product))
        dim_by_key = {d.dimension_key: d for d in all_dims}

        # 1. 校验必填维度齐全
        missing = [
            d.dimension_key for d in all_dims
            if d.is_required and d.dimension_key not in selections
        ]
        if missing:
            return {
                'valid': False,
                'price': None,
                'missing_dimensions': missing,
                'invalid_selections': [],
                'breakdown': {},
                'reason': '缺少必填配置维度',
            }

        # 2. 校验每个 selection 的维度合法性 + 选项归属
        invalid: list = []
        for key, value in selections.items():
            dim = dim_by_key.get(key)
            if dim is None:
                invalid.append({
                    'dimension_key': key,
                    'option_key': value,
                    'reason': f'维度 {key} 不属于该产品',
                })
                continue
            allowed = PriceCalculationService._option_keys(dim)
            if allowed and value not in allowed:
                invalid.append({
                    'dimension_key': key,
                    'option_key': value,
                    'reason': f'选项 {value} 不在维度 {key} 的允许列表 {allowed}',
                })
        if invalid:
            return {
                'valid': False,
                'price': None,
                'missing_dimensions': [],
                'invalid_selections': invalid,
                'breakdown': {},
                'reason': '存在非法选项',
            }

        # 3. 校验级联约束
        # parent_dimension 格式：
        #   "parent_key"               — 仅要求父维度已选（任意值）
        #   "parent_key=parent_value"  — 要求父维度已选且值等于 parent_value
        for dim in all_dims:
            if not dim.parent_dimension:
                continue
            if dim.dimension_key not in selections:
                # 子维度可选；用户没选则不约束
                continue
            parent_parts = dim.parent_dimension.split('=', 1)
            parent_key = parent_parts[0].strip()
            required_parent_value = parent_parts[1].strip() if len(parent_parts) == 2 else None

            if parent_key not in selections:
                return {
                    'valid': False,
                    'price': None,
                    'missing_dimensions': [parent_key],
                    'invalid_selections': [],
                    'breakdown': {},
                    'reason': f'维度 {dim.dimension_key} 依赖 {parent_key}，请先选择',
                }
            if required_parent_value is not None and selections[parent_key] != required_parent_value:
                return {
                    'valid': False,
                    'price': None,
                    'missing_dimensions': [],
                    'invalid_selections': [{
                        'dimension_key': dim.dimension_key,
                        'option_key': selections[dim.dimension_key],
                        'reason': (
                            f'维度 {dim.dimension_key} 仅在 {parent_key}={required_parent_value} '
                            f'时可选，但当前 {parent_key}={selections[parent_key]}'
                        ),
                    }],
                    'breakdown': {},
                    'reason': '级联约束不满足',
                }

        # 3. 模式 A：查映射表
        if product.pricing_mode == 'MATRIX':
            sig = ProductPriceMatrix.build_signature(selections)
            row = ProductPriceMatrix.objects.filter(
                product=product, config_signature=sig
            ).first()
            if not row:
                return {
                    'valid': False,
                    'price': None,
                    'missing_dimensions': [],
                    'invalid_selections': [],
                    'breakdown': selections,
                    'reason': '该配置组合无对应价格',
                }
            return {
                'valid': True,
                'price': row.price,
                'missing_dimensions': [],
                'invalid_selections': [],
                'breakdown': selections,
                'reason': '',
            }

        # 4. 模式 B：基准价 + 加价
        base = product.base_price or Decimal('0')
        price = base
        deltas = []
        for k, v in selections.items():
            rule = ProductPriceRule.objects.filter(
                product=product, dimension_key=k, option_key=v
            ).first()
            if rule:
                price += rule.price_delta
                deltas.append({'dimension': k, 'option': v, 'delta': str(rule.price_delta)})
        return {
            'valid': True,
            'price': price,
            'missing_dimensions': [],
            'invalid_selections': [],
            'breakdown': {'base_price': str(base), 'deltas': deltas},
            'reason': '',
        }


# ─── 产品配置 Excel 导入服务 ──────────────────────────────────────────────────

class ConfigExcelService:
    """产品配置 Excel 导入（OPT-6）"""

    @staticmethod
    def generate_template() -> bytes:
        """生成标准配置 Excel 模板"""
        wb = openpyxl.Workbook()

        # Sheet 1: dimensions
        ws1 = wb.active
        ws1.title = 'dimensions'
        ws1.append(['dimension_key', 'dimension_label', 'options', 'parent_dimension', 'is_required', 'sort_order'])
        ws1.append(['frame_color_back', '框架颜色（背框）', 'P1,P2,P3', '', 'TRUE', '1'])
        ws1.append(['backrest_material', '靠背材质', '网,布,皮', '', 'TRUE', '2'])
        ws1.append(['backrest_series', '靠背材质系列', 'AIR,3D knit,intermix', 'backrest_material=网', 'FALSE', '3'])
        ws1.append(['armrest', '扶手', '2D,3D,4D', '', 'TRUE', '4'])

        # Sheet 2: pricing_mode
        ws2 = wb.create_sheet('pricing_mode')
        ws2.append(['mode', 'base_price'])
        ws2.append(['MATRIX', ''])

        # Sheet 3a: matrix
        ws3 = wb.create_sheet('matrix')
        ws3.append(['frame_color_back', 'backrest_material', 'backrest_series', 'armrest', 'price'])
        ws3.append(['P1', '网', 'AIR', '3D', '2580'])

        # Sheet 3b: rules
        ws4 = wb.create_sheet('rules')
        ws4.append(['dimension_key', 'option_key', 'price_delta'])
        ws4.append(['frame_color_back', 'P1', '0'])
        ws4.append(['frame_color_back', 'P2', '50'])
        ws4.append(['backrest_material', '皮', '800'])

        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.getvalue()

    @staticmethod
    def parse_excel(product: Product, file) -> dict:
        """
        解析上传的配置 Excel，返回预览结果。
        返回: {
            'pricing_mode': 'MATRIX'|'RULE',
            'base_price': Decimal|None,
            'dimensions': [...],
            'price_entries': [...],
            'errors': [...],
            'success_count': int,
            'failed_count': int,
        }
        """
        wb = openpyxl.load_workbook(file, read_only=True)
        errors = []
        result = {
            'pricing_mode': 'MATRIX',
            'base_price': None,
            'dimensions': [],
            'price_entries': [],
            'errors': errors,
            'success_count': 0,
            'failed_count': 0,
        }

        # Parse pricing_mode sheet
        if 'pricing_mode' in wb.sheetnames:
            ws = wb['pricing_mode']
            rows = list(ws.iter_rows(min_row=2, values_only=True))
            if rows and rows[0]:
                mode = str(rows[0][0] or 'MATRIX').strip().upper()
                if mode in ('MATRIX', 'RULE'):
                    result['pricing_mode'] = mode
                base = rows[0][1] if len(rows[0]) > 1 else None
                if base:
                    try:
                        result['base_price'] = Decimal(str(base))
                    except Exception:
                        errors.append('pricing_mode sheet: base_price 格式错误')

        # Parse dimensions sheet
        if 'dimensions' in wb.sheetnames:
            ws = wb['dimensions']
            rows = list(ws.iter_rows(min_row=1, values_only=True))
            if len(rows) > 1:
                headers = [str(h or '').strip() for h in rows[0]]
                for i, row in enumerate(rows[1:], start=2):
                    data = dict(zip(headers, row))
                    dim_key = str(data.get('dimension_key', '') or '').strip()
                    if not dim_key:
                        errors.append(f'dimensions sheet 第{i}行: dimension_key 为空')
                        continue
                    options_raw = str(data.get('options', '') or '').strip()
                    options = [{'key': o.strip(), 'label': o.strip()} for o in options_raw.split(',') if o.strip()]
                    result['dimensions'].append({
                        'dimension_key': dim_key,
                        'dimension_label': str(data.get('dimension_label', '') or dim_key).strip(),
                        'options': options,
                        'parent_dimension': str(data.get('parent_dimension', '') or '').strip(),
                        'is_required': str(data.get('is_required', 'TRUE')).strip().upper() == 'TRUE',
                        'sort_order': int(data.get('sort_order', 0) or 0),
                    })

        # Parse matrix or rules sheet
        if result['pricing_mode'] == 'MATRIX' and 'matrix' in wb.sheetnames:
            ws = wb['matrix']
            rows = list(ws.iter_rows(min_row=1, values_only=True))
            if len(rows) > 1:
                headers = [str(h or '').strip() for h in rows[0]]
                price_col = headers.index('price') if 'price' in headers else -1
                dim_headers = [h for h in headers if h != 'price']
                for i, row in enumerate(rows[1:], start=2):
                    data = dict(zip(headers, row))
                    try:
                        price = Decimal(str(data.get('price', 0)))
                    except Exception:
                        errors.append(f'matrix sheet 第{i}行: price 格式错误')
                        result['failed_count'] += 1
                        continue
                    config = {h: str(data.get(h, '') or '').strip() for h in dim_headers}
                    result['price_entries'].append({'config': config, 'price': price})
                    result['success_count'] += 1

        elif result['pricing_mode'] == 'RULE' and 'rules' in wb.sheetnames:
            ws = wb['rules']
            rows = list(ws.iter_rows(min_row=1, values_only=True))
            if len(rows) > 1:
                for i, row in enumerate(rows[1:], start=2):
                    if len(row) < 3:
                        errors.append(f'rules sheet 第{i}行: 列数不足')
                        result['failed_count'] += 1
                        continue
                    dim_key = str(row[0] or '').strip()
                    opt_key = str(row[1] or '').strip()
                    try:
                        delta = Decimal(str(row[2]))
                    except Exception:
                        errors.append(f'rules sheet 第{i}行: price_delta 格式错误')
                        result['failed_count'] += 1
                        continue
                    result['price_entries'].append({
                        'dimension_key': dim_key,
                        'option_key': opt_key,
                        'price_delta': delta,
                    })
                    result['success_count'] += 1

        return result

    @staticmethod
    @transaction.atomic
    def execute_import(product: Product, parsed: dict):
        """确认导入：先清空后写入"""
        # 更新产品定价模式
        product.pricing_mode = parsed['pricing_mode']
        if parsed['base_price'] is not None:
            product.base_price = parsed['base_price']
        product.save(update_fields=['pricing_mode', 'base_price'])

        # 清空旧数据
        ProductConfigDimension.objects.filter(product=product).delete()
        ProductPriceMatrix.objects.filter(product=product).delete()
        ProductPriceRule.objects.filter(product=product).delete()

        # 写入维度
        for dim in parsed['dimensions']:
            ProductConfigDimension.objects.create(
                product=product,
                dimension_key=dim['dimension_key'],
                dimension_label=dim['dimension_label'],
                options=dim['options'],
                parent_dimension=dim['parent_dimension'],
                is_required=dim['is_required'],
                sort_order=dim['sort_order'],
            )

        # 写入价格数据
        if parsed['pricing_mode'] == 'MATRIX':
            for entry in parsed['price_entries']:
                sig = ProductPriceMatrix.build_signature(entry['config'])
                ProductPriceMatrix.objects.create(
                    product=product,
                    config_signature=sig,
                    config_attributes=entry['config'],
                    price=entry['price'],
                )
        else:  # RULE
            for i, entry in enumerate(parsed['price_entries']):
                ProductPriceRule.objects.create(
                    product=product,
                    dimension_key=entry['dimension_key'],
                    option_key=entry['option_key'],
                    price_delta=entry['price_delta'],
                    sort_order=i,
                )

        # 更新 min_price（取最低价格）
        if parsed['pricing_mode'] == 'MATRIX' and parsed['price_entries']:
            min_p = min(e['price'] for e in parsed['price_entries'])
            product.min_price = min_p
            product.save(update_fields=['min_price'])


# ─── 类别选项服务 ─────────────────────────────────────────────────────────────

class CategoryOptionsService:
    """一级 + 二级类别枚举（6 大类，中文标签）"""

    # 一级类别中文标签
    L1_LABELS = {
        'SEATING': '坐具类',
        'DESKS_WORKSTATIONS': '工位办公桌类',
        'TABLE': '桌台类',
        'STORAGE': '收纳储物类',
        'ACCESSORIES': '配套附件类',
        'EDUCATION': '教育家具类',
    }

    # 一级 → 二级映射（key 稳定英文，label 中文）
    L1_L2_MAP = {
        'SEATING': [
            ('OFFICE_CHAIR', '办公椅'),
            ('GUEST_CHAIR', '访客椅'),
            ('CONFERENCE_CHAIR', '会议椅'),
            ('STOOL', '凳子'),
            ('LOUNGE_SEATING', '休闲坐具'),
            ('VISITOR_SEATING', '接待椅'),
            ('OPERATOR_SEATING', '职员椅'),
        ],
        'DESKS_WORKSTATIONS': [
            ('DESK', '办公桌'),
            ('HEIGHT_ADJUSTABLE_DESK', '升降桌'),
            ('BENCHING', '屏风工位'),
            ('PRIVATE_OFFICE', '独立办公室办公桌'),
        ],
        'TABLE': [
            ('CONFERENCE_TABLE', '会议/协作桌'),
            ('OCCASIONAL_TABLE', '休闲桌'),
            ('OUTDOOR_TABLE', '户外桌及遮阳设施'),
        ],
        'STORAGE': [
            ('WORKSTATION_STORAGE', '工位收纳'),
            ('LOCKER', '储物柜'),
            ('CABINET_CREDENZA', '文件柜/矮柜'),
            ('BOOKCASE_SHELVING', '书柜/置物架'),
            ('CART', '移动推车'),
        ],
        'ACCESSORIES': [
            ('MODULAR_WALL', '模块化隔断及隔音材料'),
            ('POD', '独立 Pod 单元'),
            ('FREESTANDING_SCREEN', '独立屏风'),
            ('SPACE_DIVISION', '建筑/空间分割件'),
            ('MONITOR_ARM', '显示器支架及配件'),
            ('CABLE_MANAGEMENT', '电源/线缆管理'),
            ('LIGHTING', '照明设备'),
            ('ACC_TABLE', '附属桌台配件'),
        ],
        'EDUCATION': [
            ('CLASSROOM_CHAIR', '教室椅'),
            ('EDUCATION_LOUNGE', '教育休闲家具'),
            ('EDU_SEATING', '教育类坐具'),
            ('CLASSROOM_STORAGE', '教室收纳'),
            ('EDU_DESK', '教育类工位桌'),
            ('EDU_ACCESSORY', '教育类附件'),
        ],
    }

    @classmethod
    def get_options(cls) -> dict:
        l1_options = [{'value': k, 'label': cls.L1_LABELS.get(k, k)} for k in cls.L1_L2_MAP.keys()]
        l2_options = {}
        for l1, items in cls.L1_L2_MAP.items():
            l2_options[l1] = [{'value': v, 'label': label} for v, label in items]
        return {'category_l1': l1_options, 'category_l2': l2_options}


# ─── 批量产品导入（长格式，多产品单表） ──────────────────────────────────────

class BatchProductImportService:
    """
    批量产品导入 —— 采用客户长格式（竖排），支持一次导入多个产品。

    模板两个 Sheet：
      「产品」   : 产品类别 | 编号 | 一级分类 | 二级分类 | 品牌 | 产地 | 货期 | 形状 | 定价模式 | 描述
      「配置参数」: 产品类别 | 配置大类 | 部件/材质 | 规格/代码 | 价格 | 是否默认配置

    规则：
      - 「产品」每行 → 幂等创建/更新 Product（按编号优先，否则按名称匹配 name=产品类别）。
      - 「配置参数」按 (产品类别, 配置大类) 分组 → 每个配置大类 = 一个 ProductConfigDimension，
        行 = 选项（规格/代码 作 key，部件/材质+规格/代码 作 label）。
      - "配置款式" 类的行 → ProductConfigPreset（code=规格/代码，label=部件/材质）。
      - 是否默认配置=TRUE → 标记默认预设 / 默认选项。
      - 价格列可空：填了价则写入 ProductPriceRule（dimension_key, option_key, price_delta=价格）作为
        结构化留存；最终整机查表定价以后续确认的价格表为准。
    """

    ORIGIN_MAP = {'进口': 'IMPORT', '国产': 'DOMESTIC', 'IMPORT': 'IMPORT', 'DOMESTIC': 'DOMESTIC'}
    PRODUCT_SHEET = '产品'
    CONFIG_SHEET = '配置参数'
    STYLE_DIMENSION_KEYS = ('配置款式', '款式')  # 视为预设款式的配置大类名

    @staticmethod
    def _truthy(v) -> bool:
        return str(v or '').strip().upper() in ('TRUE', '1', '是', 'Y', 'YES', '默认')

    @classmethod
    def generate_template(cls) -> bytes:
        wb = openpyxl.Workbook()
        ws1 = wb.active
        ws1.title = cls.PRODUCT_SHEET
        ws1.append(['产品类别', '编号', '一级分类', '二级分类', '品牌', '产地', '货期', '形状', '定价模式', '描述'])
        ws1.append(['Leader 升降经理桌', 'ZK-LEADER-01', 'DESKS_WORKSTATIONS', 'HEIGHT_ADJUSTABLE_DESK',
                    'ZIKOO', '国产', 'WITHIN_45D', '方形', 'MATRIX', '示例产品'])

        ws2 = wb.create_sheet(cls.CONFIG_SHEET)
        ws2.append(['产品类别', '配置大类', '部件/材质', '规格/代码', '价格', '是否默认配置'])
        ws2.append(['Leader 升降经理桌', '桌板材质', '科技木皮', 'VT-01 科技浅橡木', '', ''])
        ws2.append(['Leader 升降经理桌', '产品规格', '规格21', 'W2100*D1800*H650/1250', '', 'TRUE'])
        ws2.append(['Leader 升降经理桌', '配置款式', 'WW', '白色钢脚+白色边框+木皮台面', '', 'TRUE'])

        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.getvalue()

    @classmethod
    def parse(cls, file) -> dict:
        wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
        errors = []
        products = {}  # name -> meta dict

        # 解析「产品」sheet
        if cls.PRODUCT_SHEET not in wb.sheetnames:
            errors.append(f'缺少「{cls.PRODUCT_SHEET}」sheet')
        else:
            ws = wb[cls.PRODUCT_SHEET]
            rows = list(ws.iter_rows(min_row=1, values_only=True))
            if len(rows) > 1:
                headers = [str(h or '').strip() for h in rows[0]]
                for i, row in enumerate(rows[1:], start=2):
                    data = dict(zip(headers, row))
                    name = str(data.get('产品类别', '') or '').strip()
                    if not name:
                        continue
                    products[name] = {
                        'name': name,
                        'code': str(data.get('编号', '') or '').strip() or None,
                        'category_l1': str(data.get('一级分类', '') or '').strip() or 'SEATING',
                        'category_l2': str(data.get('二级分类', '') or '').strip(),
                        'brand': str(data.get('品牌', '') or '').strip(),
                        'origin': cls.ORIGIN_MAP.get(str(data.get('产地', '') or '').strip(), 'DOMESTIC'),
                        'lead_time': str(data.get('货期', '') or '').strip(),
                        'shape': str(data.get('形状', '') or '').strip(),
                        'pricing_mode': (str(data.get('定价模式', '') or 'MATRIX').strip().upper()
                                         if str(data.get('定价模式', '') or '').strip().upper() in ('MATRIX', 'RULE')
                                         else 'MATRIX'),
                        'description': str(data.get('描述', '') or '').strip(),
                        'dimensions': {},   # 配置大类 -> [ {key,label,price,is_default}, ... ]
                        'presets': [],      # [ {code,label,is_default} ]
                    }

        # 解析「配置参数」sheet
        if cls.CONFIG_SHEET not in wb.sheetnames:
            errors.append(f'缺少「{cls.CONFIG_SHEET}」sheet')
        else:
            ws = wb[cls.CONFIG_SHEET]
            rows = list(ws.iter_rows(min_row=1, values_only=True))
            if len(rows) > 1:
                headers = [str(h or '').strip() for h in rows[0]]
                for i, row in enumerate(rows[1:], start=2):
                    data = dict(zip(headers, row))
                    pname = str(data.get('产品类别', '') or '').strip()
                    big = str(data.get('配置大类', '') or '').strip()
                    part = str(data.get('部件/材质', '') or '').strip()
                    code = str(data.get('规格/代码', '') or '').strip()
                    price_raw = data.get('价格')
                    is_default = cls._truthy(data.get('是否默认配置'))
                    if not pname or not big:
                        continue
                    if pname not in products:
                        # 「产品」sheet 未声明的产品，自动补一个占位
                        products[pname] = {
                            'name': pname, 'code': None, 'category_l1': 'SEATING', 'category_l2': '',
                            'brand': '', 'origin': 'DOMESTIC', 'lead_time': '', 'shape': '',
                            'pricing_mode': 'MATRIX', 'description': '',
                            'dimensions': {}, 'presets': [],
                        }
                    p = products[pname]
                    price = None
                    if price_raw not in (None, ''):
                        try:
                            price = Decimal(str(price_raw))
                        except Exception:
                            errors.append(f'{cls.CONFIG_SHEET} 第{i}行: 价格格式错误({price_raw})')
                    opt_key = code or part
                    opt_label = (f'{code} {part}'.strip() if code and part else (code or part))
                    if big in cls.STYLE_DIMENSION_KEYS:
                        p['presets'].append({'code': opt_key, 'label': part or code, 'is_default': is_default})
                    else:
                        p['dimensions'].setdefault(big, [])
                        p['dimensions'][big].append({
                            'key': opt_key, 'label': opt_label, 'price': price, 'is_default': is_default,
                        })

        summary = {
            'product_count': len(products),
            'products': [
                {
                    'name': p['name'], 'code': p['code'],
                    'dimension_count': len(p['dimensions']),
                    'option_count': sum(len(v) for v in p['dimensions'].values()),
                    'preset_count': len(p['presets']),
                }
                for p in products.values()
            ],
            'errors': errors,
        }
        return {'products': products, 'summary': summary, 'errors': errors}

    @classmethod
    @transaction.atomic
    def execute_import(cls, parsed: dict, user):
        from .models import Brand as _Brand
        created, updated = 0, 0
        for meta in parsed['products'].values():
            # 品牌
            brand = None
            if meta['brand']:
                brand, _ = _Brand.objects.get_or_create(name=meta['brand'])
            # 产品（编号优先匹配）
            product = None
            if meta['code']:
                product = Product.objects.filter(code=meta['code']).first()
            if not product:
                product = Product.objects.filter(name=meta['name']).first()
            fields = dict(
                name=meta['name'], code=meta['code'],
                category_l1=meta['category_l1'], category_l2=meta['category_l2'],
                brand=brand, origin=meta['origin'], lead_time=meta['lead_time'],
                shape=meta['shape'], pricing_mode=meta['pricing_mode'],
                description=meta['description'],
            )
            if product:
                for k, v in fields.items():
                    setattr(product, k, v)
                product.save()
                updated += 1
            else:
                product = Product.objects.create(created_by=user, **fields)
                created += 1

            # 重建维度 / 价格 / 预设
            ProductConfigDimension.objects.filter(product=product).delete()
            ProductPriceRule.objects.filter(product=product).delete()
            ProductConfigPreset.objects.filter(product=product).delete()

            for order, (big, opts) in enumerate(meta['dimensions'].items()):
                ProductConfigDimension.objects.create(
                    product=product, dimension_key=big, dimension_label=big,
                    options=[{'key': o['key'], 'label': o['label']} for o in opts],
                    is_required=True, sort_order=order,
                )
                for o in opts:
                    if o['price'] is not None:
                        ProductPriceRule.objects.create(
                            product=product, dimension_key=big, option_key=o['key'],
                            price_delta=o['price'],
                        )
            for order, preset in enumerate(meta['presets']):
                ProductConfigPreset.objects.create(
                    product=product, code=preset['code'], label=preset['label'],
                    selections={}, is_default=preset['is_default'], sort_order=order,
                )
        return {'created': created, 'updated': updated}


# ─── 产品配置导出 ─────────────────────────────────────────────────────────────

class ConfigExportService:
    """导出单个产品当前配置数据为 Excel（PM-6）"""

    @staticmethod
    def export(product: Product) -> bytes:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'dimensions'
        ws.append(['dimension_key', 'dimension_label', 'options', 'parent_dimension', 'is_required', 'sort_order'])
        for d in product.config_dimensions.all():
            opts = ','.join(
                (o.get('key', '') if isinstance(o, dict) else str(o)) for o in (d.options or [])
            )
            ws.append([d.dimension_key, d.dimension_label, opts, d.parent_dimension,
                       'TRUE' if d.is_required else 'FALSE', d.sort_order])

        ws2 = wb.create_sheet('pricing')
        if product.pricing_mode == 'MATRIX':
            ws2.append(['config_signature', 'config_attributes', 'price'])
            for m in product.price_matrix.all():
                ws2.append([m.config_signature, json.dumps(m.config_attributes, ensure_ascii=False), str(m.price)])
        else:
            ws2.append(['dimension_key', 'option_key', 'price_delta'])
            for r in product.price_rules.all():
                ws2.append([r.dimension_key, r.option_key, str(r.price_delta)])

        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.getvalue()
