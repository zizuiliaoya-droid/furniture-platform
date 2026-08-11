"""Product management views."""
import json

import openpyxl
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from auth_app.permissions import HasModulePermission, IsAdminRole, require_module_permission
from .models import (
    Brand, Category, Product, ProductConfig, ProductConfigDimension,
    ProductDocument, ProductImage,
)
from .serializers import (
    BrandSerializer, CalculatePriceSerializer,
    CategorySerializer, CategoryTreeSerializer,
    ProductConfigDimensionSerializer, ProductConfigDimensionWriteSerializer,
    ProductCompositeCreateSerializer,
    ProductConfigSerializer, ProductCreateUpdateSerializer,
    ProductDetailSerializer, ProductDocumentCreateSerializer,
    ProductDocumentSerializer, ProductImageSerializer, ProductListSerializer,
)
from .services import (
    CategoryOptionsService, CategoryService, ConfigExcelService,
    ConfigExportService, BatchProductImportService, CustomerWorkbookImportService,
    DimensionMutationService, FlexibleConfigExcelService, SafeConfigExportService,
    PriceCalculationService, ProductCompositeService,
    ProductImageService, ProductImportService,
)


# ─── Brand ViewSet ────────────────────────────────────────────────────────────

class BrandViewSet(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'PRODUCT'


# ─── Product ViewSet ──────────────────────────────────────────────────────────

class ProductViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'PRODUCT'
    permission_action_map = {
        'reactivate': 'update',
        'upload_images': 'update',
        'update_image_order': 'update',
        'import_products': 'create',
        'download_import_template': 'export',
        'config_dimensions': 'view',
        'add_config_dimension': 'update',
        'config_dimension_detail': {'GET': 'view', 'PATCH': 'update', 'DELETE': 'update'},
        'config_dimension_impact': 'view',
        'calculate_price': 'view',
        'upload_config_excel': 'update',
        'download_config_template': 'export',
        'product_documents': {'GET': 'view', 'POST': 'update'},
        'remove_product_document': 'update',
        'create_composite': 'create',
        'category_options': 'view',
        'batch_import': 'create',
        'download_batch_template': 'export',
        'export_config': 'export',
    }

    def get_queryset(self):
        qs = Product.objects.select_related('brand', 'created_by').prefetch_related(
            'images', 'configs', 'config_dimensions'
        )
        if not getattr(self.request.user, 'is_admin', False):
            qs = qs.filter(is_active=True)

        # 搜索
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(code__icontains=search) |
                Q(description__icontains=search) |
                Q(configs__config_name__icontains=search) |
                Q(configs__attributes__icontains=search)
            ).distinct()

        # 筛选
        origin = self.request.query_params.get('origin')
        if origin:
            qs = qs.filter(origin=origin)
        category_l1 = self.request.query_params.get('category_l1')
        if category_l1:
            qs = qs.filter(category_l1=category_l1)
        category_l2 = self.request.query_params.get('category_l2')
        if category_l2:
            qs = qs.filter(category_l2=category_l2)
        brand = self.request.query_params.get('brand')
        if brand:
            qs = qs.filter(brand_id=brand)
        lead_time = self.request.query_params.get('lead_time')
        if lead_time:
            qs = qs.filter(lead_time=lead_time)
        min_price = self.request.query_params.get('min_price')
        if min_price:
            qs = qs.filter(min_price__gte=min_price)
        max_price = self.request.query_params.get('max_price')
        if max_price:
            qs = qs.filter(min_price__lte=max_price)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None and getattr(self.request.user, 'is_admin', False):
            qs = qs.filter(is_active=is_active.lower() == 'true')

        # 旧分类兼容
        category = self.request.query_params.get('category')
        if category:
            cat = Category.objects.filter(pk=category).first()
            if cat:
                cat_ids = [cat.id] + list(cat.children.values_list('id', flat=True))
                qs = qs.filter(Q(category_id__in=cat_ids) | Q(categories__id__in=cat_ids)).distinct()

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        # 始终使用模块权限矩阵；action 装饰器中的历史管理员覆盖不再绕过矩阵。
        return [IsAuthenticated(), HasModulePermission()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        # ?hard=true 永久删除；否则软删除（下架）
        if self.request.query_params.get('hard') == 'true':
            instance.delete()
        else:
            instance.is_active = False
            instance.save(update_fields=['is_active'])

    @action(detail=True, methods=['post'], url_path='reactivate',
            permission_classes=[IsAuthenticated, IsAdminRole])
    def reactivate(self, request, pk=None):
        """重新上架（下架产品恢复为上架）"""
        product = self.get_object()
        product.is_active = True
        product.save(update_fields=['is_active'])
        return Response({'detail': 'ok', 'is_active': True})

    # ─── 图片管理 ─────────────────────────────────────────────────────────────

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminRole])
    def upload_images(self, request, pk=None):
        product = self.get_object()
        files = request.FILES.getlist('images')
        if not files:
            return Response({'detail': '请选择图片'}, status=status.HTTP_400_BAD_REQUEST)
        images = ProductImageService.upload_images(product, files)
        return Response(ProductImageSerializer(images, many=True).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='images/order', permission_classes=[IsAuthenticated, IsAdminRole])
    def update_image_order(self, request, pk=None):
        product = self.get_object()
        order = request.data.get('order', [])
        for i, img_id in enumerate(order):
            ProductImage.objects.filter(pk=img_id, product=product).update(sort_order=i)
        return Response({'detail': 'ok'})

    # ─── 产品批量导入（旧） ───────────────────────────────────────────────────

    @action(detail=False, methods=['post'], url_path='import', permission_classes=[IsAuthenticated, IsAdminRole])
    def import_products(self, request):
        file = request.FILES.get('file')
        if not file or not file.name.endswith('.xlsx'):
            return Response({'detail': '请上传 .xlsx 格式文件'}, status=status.HTTP_400_BAD_REQUEST)
        result = ProductImportService.parse_excel(file)
        if request.query_params.get('confirm') == 'true' and result.get('parsed_data'):
            count = ProductImportService.execute_import(result['parsed_data'], request.user)
            return Response({'imported_count': count})
        return Response({
            'success_count': result['success_count'],
            'failed_count': result['failed_count'],
            'preview': [{'row': r['row'], 'name': r['name'], 'errors': r['errors']} for r in result['preview']],
        })

    @action(detail=False, methods=['get'], url_path='import/template', permission_classes=[IsAuthenticated, IsAdminRole])
    def download_import_template(self, request):
        content = ProductImportService.generate_template()
        resp = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="product_import_template.xlsx"'
        return resp

    # ─── 配置维度 ─────────────────────────────────────────────────────────────

    @action(detail=True, methods=['get'], url_path='config-dimensions')
    def config_dimensions(self, request, pk=None):
        product = self.get_object()
        dims = product.config_dimensions.all()
        return Response(ProductConfigDimensionSerializer(dims, many=True).data)

    @action(detail=True, methods=['post'], url_path='config-dimensions/add')
    def add_config_dimension(self, request, pk=None):
        product = self.get_object()
        serializer = ProductConfigDimensionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'patch', 'delete'],
            url_path=r'config-dimensions/(?P<dimension_id>[^/.]+)')
    def config_dimension_detail(self, request, pk=None, dimension_id=None):
        product = self.get_object()
        dimension = ProductConfigDimension.objects.filter(
            product=product, pk=dimension_id).first()
        if not dimension:
            return Response({'detail': '配置维度不存在'}, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            return Response(ProductConfigDimensionSerializer(dimension).data)
        if request.method == 'PATCH':
            serializer = ProductConfigDimensionWriteSerializer(
                dimension, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            try:
                updated = DimensionMutationService.update(
                    product, dimension.id, serializer.validated_data)
            except ValueError as exc:
                return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(ProductConfigDimensionSerializer(updated).data)
        force = str(request.query_params.get('force', '')).lower() == 'true'
        try:
            result = DimensionMutationService.delete(product, dimension.id, force=force)
        except ValueError as exc:
            impact = DimensionMutationService.impact(dimension)
            return Response({'detail': str(exc), 'impact': impact}, status=status.HTTP_409_CONFLICT)
        return Response(result)

    @action(detail=True, methods=['get'],
            url_path=r'config-dimensions/(?P<dimension_id>[^/.]+)/impact')
    def config_dimension_impact(self, request, pk=None, dimension_id=None):
        product = self.get_object()
        dimension = ProductConfigDimension.objects.filter(
            product=product, pk=dimension_id).first()
        if not dimension:
            return Response({'detail': '配置维度不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DimensionMutationService.impact(dimension))

    # ─── 价格计算 ─────────────────────────────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='calculate-price')
    def calculate_price(self, request, pk=None):
        product = self.get_object()
        serializer = CalculatePriceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selections = serializer.validated_data['selections']
        result = PriceCalculationService.calculate(product, selections)
        # 将 Decimal 转为 str 以便 JSON 序列化
        if result['price'] is not None:
            result['price'] = str(result['price'])
        return Response(result)

    # ─── 配置 Excel 导入 ──────────────────────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='upload-config-excel')
    def upload_config_excel(self, request, pk=None):
        product = self.get_object()
        file = request.FILES.get('file')
        if not file or not file.name.lower().endswith('.xlsx'):
            return Response({'detail': '请上传 .xlsx 格式文件'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            raw_mapping = request.data.get('mapping', '{}')
            mapping = json.loads(raw_mapping) if isinstance(raw_mapping, str) else (raw_mapping or {})
            parsed = FlexibleConfigExcelService.parse_excel(product, file, mapping=mapping)
        except (ValueError, TypeError, json.JSONDecodeError, openpyxl.utils.exceptions.InvalidFileException) as exc:
            return Response({'detail': f'Excel 解析失败：{exc}'}, status=status.HTTP_400_BAD_REQUEST)

        if request.query_params.get('confirm') == 'true':
            if parsed['errors'] or parsed.get('needs_mapping'):
                return Response({
                    'detail': '存在错误或尚未完成字段映射，无法导入',
                    'errors': parsed['errors'], 'warnings': parsed.get('warnings', []),
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                result = FlexibleConfigExcelService.execute_import(
                    product, parsed,
                    replace_dimensions=str(request.data.get('replace_dimensions', '')).lower() == 'true',
                    replace_prices=str(request.data.get('replace_prices', 'true')).lower() == 'true',
                )
            except ValueError as exc:
                return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': '导入成功', **result})

        return Response({
            'pricing_mode': parsed['pricing_mode'],
            'base_price': str(parsed['base_price']) if parsed['base_price'] is not None else None,
            'dimensions_count': len(parsed['dimensions']),
            'dimensions': parsed['dimensions'],
            'price_entries_count': parsed['success_count'],
            'preset_count': len(parsed.get('presets', [])),
            'failed_count': parsed['failed_count'],
            'detected_format': parsed.get('detected_format'),
            'needs_mapping': parsed.get('needs_mapping', False),
            'available_sheets': parsed.get('available_sheets', []),
            'impact': parsed.get('impact', {}),
            'errors': parsed['errors'],
            'warnings': parsed.get('warnings', []),
        })

    @action(detail=False, methods=['get'], url_path='config-template')
    def download_config_template(self, request):
        content = ConfigExcelService.generate_template()
        resp = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="product_config_template.xlsx"'
        return resp

    # ─── 产品-文档关联 ────────────────────────────────────────────────────────

    @action(detail=True, methods=['get', 'post'], url_path='documents')
    def product_documents(self, request, pk=None):
        product = self.get_object()
        if request.method == 'GET':
            qs = product.product_documents.select_related('document').all()
            relation_type = request.query_params.get('relation_type')
            if relation_type:
                qs = qs.filter(relation_type=relation_type)
            return Response(ProductDocumentSerializer(qs, many=True).data)
        else:
            # POST - 关联文档；写权限已由 HasModulePermission 在入口校验。
            serializer = ProductDocumentCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            from documents.models import Document
            doc = Document.objects.filter(pk=serializer.validated_data['document_id']).first()
            if not doc:
                return Response({'detail': '文档不存在'}, status=status.HTTP_404_NOT_FOUND)
            pd, created = ProductDocument.objects.get_or_create(
                product=product, document=doc,
                defaults={'relation_type': serializer.validated_data['relation_type']}
            )
            if not created:
                pd.relation_type = serializer.validated_data['relation_type']
                pd.save(update_fields=['relation_type'])
            return Response(ProductDocumentSerializer(pd).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path=r'documents/(?P<doc_id>\d+)',
            permission_classes=[IsAuthenticated, IsAdminRole])
    def remove_product_document(self, request, pk=None, doc_id=None):
        product = self.get_object()
        ProductDocument.objects.filter(product=product, document_id=doc_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ─── 事务化产品组合创建 ──────────────────────────────────────────────────

    @action(detail=False, methods=['post'], url_path='create-composite')
    def create_composite(self, request):
        try:
            raw = request.data.get('payload', '{}')
            payload = json.loads(raw) if isinstance(raw, str) else raw
        except (TypeError, json.JSONDecodeError):
            return Response({'detail': 'payload 必须是有效 JSON'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ProductCompositeCreateSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        try:
            product = ProductCompositeService.create(
                serializer.validated_data, request.user, request.FILES.getlist('images'))
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ProductDetailSerializer(product).data, status=status.HTTP_201_CREATED)

    # ─── 类别选项 ─────────────────────────────────────────────────────────────

    @action(detail=False, methods=['get'], url_path='category-options')
    def category_options(self, request):
        return Response(CategoryOptionsService.get_options())

    # ─── 批量产品导入（长格式，多产品） ───────────────────────────────────────

    @action(detail=False, methods=['post'], url_path='batch-import')
    def batch_import(self, request):
        file = request.FILES.get('file')
        if not file or not file.name.endswith('.xlsx'):
            return Response({'detail': '请上传 .xlsx 格式文件'}, status=status.HTTP_400_BAD_REQUEST)
        # 自动识别：现有“两 Sheet 长格式”或客户“每产品一 Sheet 横向格式”。
        workbook = openpyxl.load_workbook(file, read_only=True, data_only=True)
        is_long_format = {
            BatchProductImportService.PRODUCT_SHEET,
            BatchProductImportService.CONFIG_SHEET,
        }.issubset(set(workbook.sheetnames))
        workbook.close()
        file.seek(0)
        service = BatchProductImportService if is_long_format else CustomerWorkbookImportService
        parsed = service.parse(file)
        if request.query_params.get('confirm') == 'true':
            if parsed['errors']:
                return Response({'detail': '存在错误，无法导入', 'errors': parsed['errors'],
                                 'warnings': parsed.get('warnings', [])},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                result = service.execute_import(parsed, request.user)
            except ValueError as exc:
                return Response({'detail': str(exc), 'warnings': parsed.get('warnings', [])},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': '导入成功', **result})
        return Response(parsed['summary'])

    @action(detail=False, methods=['get'], url_path='batch-template')
    def download_batch_template(self, request):
        customer_format = request.query_params.get('fmt', request.query_params.get('format', 'customer')) != 'legacy'
        content = (CustomerWorkbookImportService.generate_template()
                   if customer_format else BatchProductImportService.generate_template())
        resp = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="product_customer_template.xlsx"'
        return resp

    @action(detail=True, methods=['get'], url_path='export-config')
    def export_config(self, request, pk=None):
        product = self.get_object()
        content = SafeConfigExportService.export(product)
        resp = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = f'attachment; filename="product_{product.id}_config.xlsx"'
        return resp


# ─── 独立视图函数 ─────────────────────────────────────────────────────────────

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@require_module_permission('PRODUCT', 'update')
def delete_product_image(request, pk):
    try:
        image = ProductImage.objects.get(pk=pk)
    except ProductImage.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    ProductImageService.delete_image(image)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@require_module_permission('PRODUCT', 'update')
def set_cover_image(request, pk):
    try:
        image = ProductImage.objects.select_related('product').get(pk=pk)
    except ProductImage.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    ProductImageService.set_cover(image)
    return Response(ProductImageSerializer(image).data)


# ─── 旧配置 ViewSet（兼容保留） ───────────────────────────────────────────────

class ProductConfigViewSet(ModelViewSet):
    serializer_class = ProductConfigSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'PRODUCT'

    def get_queryset(self):
        return ProductConfig.objects.filter(product_id=self.kwargs.get('product_pk'))

    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs['product_pk'])


# ─── Category ViewSet（过渡保留） ─────────────────────────────────────────────

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'PRODUCT'

    def get_queryset(self):
        qs = Category.objects.all().order_by('sort_order', 'id')
        dimension = self.request.query_params.get('dimension')
        if dimension:
            qs = qs.filter(dimension=dimension)
        parent = self.request.query_params.get('parent')
        if parent:
            qs = qs.filter(parent_id=parent)
        return qs

    @action(detail=False, methods=['get'])
    def tree(self, request):
        dimension = request.query_params.get('dimension', 'TYPE')
        roots = CategoryService.get_tree(dimension)
        return Response(CategoryTreeSerializer(roots, many=True).data)

    @action(detail=False, methods=['put'])
    def reorder(self, request):
        items = request.data.get('items', [])
        CategoryService.reorder(items)
        return Response({'detail': 'ok'})

    def perform_destroy(self, instance):
        if instance.children.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError('该分类下有子分类，无法删除')
        if instance.primary_products.exists() or instance.products.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError('该分类下有产品，无法删除')
        instance.delete()
