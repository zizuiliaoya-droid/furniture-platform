"""Catalog views - product browsing with multi-dimensional filtering."""
import json
from decimal import Decimal

from django.db.models import Q, Min, Max
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import StandardPagination
from products.models import Brand, Product, ProductConfigDimension
from products.serializers import ProductListSerializer


class CatalogBrowseView(ListAPIView):
    """图册浏览 — 多维筛选 + 多选 + MECE 区间"""
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    DYNAMIC_PREFIX = 'attr_'

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('brand').prefetch_related('images')
        params = self.request.query_params

        # 品牌（多选）
        brands = params.getlist('brand[]') or params.getlist('brand')
        if brands:
            qs = qs.filter(brand_id__in=brands)

        # 一级类别（多选）
        l1 = params.getlist('category_l1[]') or params.getlist('category_l1')
        if l1:
            qs = qs.filter(category_l1__in=l1)

        # 二级类别（多选）
        l2 = params.getlist('category_l2[]') or params.getlist('category_l2')
        if l2:
            qs = qs.filter(category_l2__in=l2)

        # 产地（多选）
        origins = params.getlist('origin[]') or params.getlist('origin')
        if origins:
            qs = qs.filter(origin__in=origins)

        # 货期（多选）
        lead_times = params.getlist('lead_time[]') or params.getlist('lead_time')
        if lead_times:
            qs = qs.filter(lead_time__in=lead_times)

        # 长度 MECE 区间
        length_range = params.get('length_range')
        if length_range:
            qs = self._apply_range_filter(qs, 'length_mm', length_range)

        # 宽度 MECE 区间
        width_range = params.get('width_range')
        if width_range:
            qs = self._apply_range_filter(qs, 'width_mm', width_range)

        # 高度 MECE 区间
        height_range = params.get('height_range')
        if height_range:
            qs = self._apply_range_filter(qs, 'height_mm', height_range)

        # 价格 MECE 区间
        price_range = params.get('price_range')
        if price_range:
            qs = self._apply_range_filter(qs, 'min_price', price_range)

        # 动态属性筛选（attr_<dimension_key>[]=value）
        # 通过产品的 config_dimensions.options 中是否包含该 value 反查产品
        # 兼容 SQLite/PostgreSQL：用 JSON 文本 icontains 匹配选项 label/key
        for raw_key, _ in params.lists():
            if not raw_key.startswith(self.DYNAMIC_PREFIX):
                continue
            dim_key = raw_key[len(self.DYNAMIC_PREFIX):].rstrip('[]')
            if not dim_key:
                continue
            values = params.getlist(raw_key)
            if not values:
                continue
            # 找出有该维度且选项包含任一指定 value 的产品
            value_q = Q()
            for v in values:
                # JSON contains 兼容写法：选项 JSON 内同时包含 value 文本
                value_q |= Q(config_dimensions__options__icontains=f'"{v}"')
            qs = qs.filter(config_dimensions__dimension_key=dim_key).filter(value_q)

        # 关键词搜索
        q = params.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(code__icontains=q) |
                Q(description__icontains=q)
            )

        return qs.distinct().order_by('-created_at')

    @staticmethod
    def _apply_range_filter(qs, field: str, range_str: str):
        """解析 MECE 区间字符串，格式: 'min-max' 或 '-max' 或 'min-'"""
        parts = range_str.split('-', 1)
        if len(parts) == 2:
            low, high = parts
            if low:
                qs = qs.filter(**{f'{field}__gte': Decimal(low) if '.' in low else int(low)})
            if high:
                qs = qs.filter(**{f'{field}__lte': Decimal(high) if '.' in high else int(high)})
        return qs


class CatalogSearchView(ListAPIView):
    """图册关键词搜索（全字段）"""
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('brand').prefetch_related('images')
        q = self.request.query_params.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(code__icontains=q) |
                Q(description__icontains=q) |
                Q(config_dimensions__options__icontains=q) |
                Q(configs__config_name__icontains=q)
            ).distinct()
        return qs.order_by('-created_at')


class CatalogFiltersView(APIView):
    """图册筛选项聚合接口"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        active_products = Product.objects.filter(is_active=True)

        # 品牌列表
        brand_ids = active_products.values_list('brand_id', flat=True).distinct()
        brands = Brand.objects.filter(id__in=brand_ids).values('id', 'name', 'is_self_owned').order_by('sort_order')

        # 一级 / 二级类别
        from products.services import CategoryOptionsService
        category_options = CategoryOptionsService.get_options()

        # 产地
        origins = [
            {'value': 'IMPORT', 'label': '进口'},
            {'value': 'DOMESTIC', 'label': '国产'},
        ]

        # 货期
        lead_times = [
            {'value': 'WITHIN_45D', 'label': '45天内'},
            {'value': '2_4M_VIETNAM', 'label': '2-4月【越南】'},
            {'value': '2_4M_MALAYSIA', 'label': '2-4月【马来西亚】'},
            {'value': '4_6M_EU', 'label': '4-6月【荷兰/意大利/德国】'},
        ]

        # MECE 区间预设
        mece_ranges = {
            'length_mm': [
                {'label': '≤600mm', 'value': '-600'},
                {'label': '600-900mm', 'value': '600-900'},
                {'label': '900-1200mm', 'value': '900-1200'},
                {'label': '1200-1800mm', 'value': '1200-1800'},
                {'label': '>1800mm', 'value': '1800-'},
            ],
            'width_mm': [
                {'label': '≤400mm', 'value': '-400'},
                {'label': '400-600mm', 'value': '400-600'},
                {'label': '600-900mm', 'value': '600-900'},
                {'label': '>900mm', 'value': '900-'},
            ],
            'height_mm': [
                {'label': '≤400mm', 'value': '-400'},
                {'label': '400-700mm', 'value': '400-700'},
                {'label': '700-1000mm', 'value': '700-1000'},
                {'label': '1000-1400mm', 'value': '1000-1400'},
                {'label': '>1400mm', 'value': '1400-'},
            ],
            'price': [
                {'label': '≤1000', 'value': '-1000'},
                {'label': '1000-3000', 'value': '1000-3000'},
                {'label': '3000-5000', 'value': '3000-5000'},
                {'label': '5000-10000', 'value': '5000-10000'},
                {'label': '>10000', 'value': '10000-'},
            ],
        }

        # 动态属性聚合（来自 ProductConfigDimension）
        dynamic_attributes = []
        dims = ProductConfigDimension.objects.filter(
            product__is_active=True
        ).values('dimension_key', 'dimension_label', 'options').distinct()

        # 按 dimension_key 聚合所有选项
        dim_map = {}
        for d in dims:
            key = d['dimension_key']
            if key not in dim_map:
                dim_map[key] = {'key': key, 'label': d['dimension_label'], 'options': set()}
            if isinstance(d['options'], list):
                for opt in d['options']:
                    if isinstance(opt, dict):
                        dim_map[key]['options'].add(opt.get('label', opt.get('key', '')))
                    else:
                        dim_map[key]['options'].add(str(opt))

        for key, info in dim_map.items():
            dynamic_attributes.append({
                'dimension_key': info['key'],
                'dimension_label': info['label'],
                'options': sorted(list(info['options'])),
            })

        return Response({
            'brands': list(brands),
            'category_l1': category_options['category_l1'],
            'category_l2': category_options['category_l2'],
            'origins': origins,
            'lead_times': lead_times,
            'mece_ranges': mece_ranges,
            'dynamic_attributes': dynamic_attributes,
        })
