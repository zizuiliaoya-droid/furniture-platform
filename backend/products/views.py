"""Product management views."""
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from auth_app.permissions import IsAdminRole
from .models import Category, Product, ProductConfig, ProductImage
from .serializers import (
    CategorySerializer, CategoryTreeSerializer,
    ProductConfigSerializer, ProductCreateUpdateSerializer,
    ProductDetailSerializer, ProductImageSerializer, ProductListSerializer,
)
from .services import CategoryService, ProductImageService, ProductImportService


class ProductViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Product.objects.select_related('category', 'created_by').prefetch_related('images', 'configs')
        if self.request.user.role != 'ADMIN':
            qs = qs.filter(is_active=True)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(code__icontains=search) |
                Q(description__icontains=search) |
                Q(configs__config_name__icontains=search) |
                Q(configs__attributes__icontains=search)
            ).distinct()
        origin = self.request.query_params.get('origin')
        if origin:
            qs = qs.filter(origin=origin)
        category = self.request.query_params.get('category')
        if category:
            cat = Category.objects.filter(pk=category).first()
            if cat:
                cat_ids = [cat.id] + list(cat.children.values_list('id', flat=True))
                qs = qs.filter(Q(category_id__in=cat_ids) | Q(categories__id__in=cat_ids)).distinct()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None and self.request.user.role == 'ADMIN':
            qs = qs.filter(is_active=is_active.lower() == 'true')
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])

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
    def download_template(self, request):
        from django.http import HttpResponse
        content = ProductImportService.generate_template()
        resp = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="product_import_template.xlsx"'
        return resp


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminRole])
def delete_product_image(request, pk):
    try:
        image = ProductImage.objects.get(pk=pk)
    except ProductImage.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    ProductImageService.delete_image(image)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminRole])
def set_cover_image(request, pk):
    try:
        image = ProductImage.objects.select_related('product').get(pk=pk)
    except ProductImage.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    ProductImageService.set_cover(image)
    return Response(ProductImageSerializer(image).data)


class ProductConfigViewSet(ModelViewSet):
    serializer_class = ProductConfigSerializer

    def get_queryset(self):
        return ProductConfig.objects.filter(product_id=self.kwargs.get('product_pk'))

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs['product_pk'])


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]

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
        dimension = request.query_params.get('dimension')
        if not dimension:
            return Response({'detail': '请指定 dimension 参数'}, status=status.HTTP_400_BAD_REQUEST)
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
