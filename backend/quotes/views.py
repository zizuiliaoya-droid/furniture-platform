"""Quote views."""
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from auth_app.permissions import HasModulePermission, IsAdminRole, has_module_permission
from django.db.models import Q as _Q

from .models import Quote, QuoteItem, QuoteShare
from .serializers import (
    AddItemFromProductSerializer, QuoteCreateUpdateSerializer,
    QuoteDetailSerializer, QuoteItemSerializer, QuoteListSerializer,
    QuoteShareSerializer,
)
from .services import QuoteService


class QuoteViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'QUOTE'
    permission_action_map = {
        'pdf': 'export', 'excel': 'export', 'shares': 'share',
        'share_candidates': 'share', 'remove_share': 'share', 'duplicate': 'create',
    }

    def get_queryset(self):
        user = self.request.user
        qs = Quote.objects.select_related('created_by').prefetch_related('items')
        # QT-7/8 可见性：管理员看全部；普通员工看自己创建的 + 被分享的
        if not getattr(user, 'is_admin', False):
            qs = qs.filter(_Q(created_by=user) | _Q(shares__shared_with=user)).distinct()
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(customer_name__icontains=search))
        s = self.request.query_params.get('status')
        if s:
            qs = qs.filter(status=s)
        # 前端"我创建的 / 分享给我的"分组过滤
        mine = self.request.query_params.get('mine')
        if mine == 'true':
            qs = qs.filter(created_by=user)
        elif mine == 'shared':
            qs = qs.filter(shares__shared_with=user).exclude(created_by=user).distinct()
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return QuoteListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return QuoteCreateUpdateSerializer
        return QuoteDetailSerializer

    def get_permissions(self):
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def _assert_owner_or_admin(self, quote):
        user = self.request.user
        if getattr(user, 'is_admin', False) or quote.created_by_id == user.id:
            return
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied('该报价单为只读（他人分享）')

    def perform_update(self, serializer):
        self._assert_owner_or_admin(serializer.instance)
        new_status = serializer.validated_data.get('status')
        if new_status and new_status != serializer.instance.status:
            if not QuoteService.validate_status_change(serializer.instance.status, new_status):
                from rest_framework.exceptions import ValidationError
                raise ValidationError(f'不允许从 {serializer.instance.status} 变更为 {new_status}')
        quote = serializer.save()
        quote.recalculate_total()

    def perform_destroy(self, instance):
        self._assert_owner_or_admin(instance)
        instance.delete()

    @action(detail=True, methods=['get', 'post'], url_path='shares')
    def shares(self, request, pk=None):
        quote = self.get_object()
        if request.method == 'GET':
            return Response(QuoteShareSerializer(quote.shares.select_related('shared_with'), many=True).data)
        self._assert_owner_or_admin(quote)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'detail': '缺少 user_id'}, status=status.HTTP_400_BAD_REQUEST)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            target = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        if target.id == request.user.id:
            return Response({'detail': '不能分享给自己'}, status=status.HTTP_400_BAD_REQUEST)
        if not target.is_active:
            return Response({'detail': '不能分享给已停用用户'}, status=status.HTTP_400_BAD_REQUEST)
        share, created = QuoteShare.objects.get_or_create(
            quote=quote, shared_with=target, defaults={'created_by': request.user})
        if not created:
            return Response({'detail': '该用户已在分享列表中'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(QuoteShareSerializer(share).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='share-candidates')
    def share_candidates(self, request, pk=None):
        """返回当前报价可分享的启用用户，避免前端依赖管理员用户管理接口。"""
        quote = self.get_object()
        self._assert_owner_or_admin(quote)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        shared_ids = quote.shares.values_list('shared_with_id', flat=True)
        candidates = User.objects.filter(is_active=True).exclude(
            pk=request.user.pk).exclude(pk__in=shared_ids).order_by('display_name', 'username')
        return Response([
            {'id': user.id, 'username': user.username, 'display_name': user.display_name}
            for user in candidates
        ])

    @action(detail=True, methods=['delete'], url_path=r'shares/(?P<user_id>\d+)')
    def remove_share(self, request, pk=None, user_id=None):
        quote = self.get_object()
        self._assert_owner_or_admin(quote)
        QuoteShare.objects.filter(quote=quote, shared_with_id=user_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        original = self.get_object()
        new_quote = QuoteService.duplicate(original.id, request.user)
        return Response(QuoteDetailSerializer(new_quote).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        quote = self.get_object()
        pdf_bytes = QuoteService.export_pdf(quote.id)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="quote_{quote.id}.pdf"'
        return response

    @action(detail=True, methods=['get'], url_path='excel')
    def excel(self, request, pk=None):
        """QT-3 导出 Excel：?fmt=sales_order|quotation

        注意：查询参数用 `fmt`，因为 DRF 保留了 `format` 参数用于内容协商。
        """
        from .services import QuoteExcelService
        quote = self.get_object()
        quote = Quote.objects.prefetch_related(
            'items', 'items__product', 'items__product__brand').get(pk=quote.pk)
        fmt = request.query_params.get('fmt', 'quotation')
        if fmt == 'sales_order':
            content = QuoteExcelService.export_sales_order(quote)
            name = f'sales_order_{pk}.xlsx'
        else:
            content = QuoteExcelService.export_quotation(quote)
            name = f'quotation_{pk}.xlsx'
        resp = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = f'attachment; filename="{name}"'
        return resp


class QuoteItemViewSet(ModelViewSet):
    serializer_class = QuoteItemSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'QUOTE'

    def get_queryset(self):
        user = self.request.user
        qs = QuoteItem.objects.select_related('quote')
        if not getattr(user, 'is_admin', False):
            qs = qs.filter(_Q(quote__created_by=user) | _Q(quote__shares__shared_with=user)).distinct()
        quote_pk = self.kwargs.get('quote_pk')
        if quote_pk:
            qs = qs.filter(quote_id=quote_pk)
        return qs

    def _check_write(self, quote):
        user = self.request.user
        if not (getattr(user, 'is_admin', False) or quote.created_by_id == user.id):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('该报价单为只读（他人分享）')
        if quote.status != 'DRAFT':
            from rest_framework.exceptions import ValidationError
            raise ValidationError('只有草稿报价单可以修改明细')

    def perform_create(self, serializer):
        try:
            quote = Quote.objects.get(pk=self.kwargs['quote_pk'])
        except Quote.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('报价单不存在')
        self._check_write(quote)
        item = serializer.save(quote=quote)
        quote.recalculate_total()

    def perform_update(self, serializer):
        self._check_write(serializer.instance.quote)
        item = serializer.save()
        item.quote.recalculate_total()

    def perform_destroy(self, instance):
        self._check_write(instance.quote)
        quote = instance.quote
        instance.delete()
        quote.recalculate_total()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item_from_product_view(request, quote_pk):
    """POST /api/quotes/{id}/items/from-product/ — 一键加入报价单。"""
    if not has_module_permission(request.user, 'QUOTE', 'create'):
        return Response({'detail': '缺少报价新增权限'}, status=status.HTTP_403_FORBIDDEN)
    try:
        quote = Quote.objects.get(pk=quote_pk)
    except Quote.DoesNotExist:
        return Response({'detail': '报价单不存在'}, status=status.HTTP_404_NOT_FOUND)
    if not (request.user.is_admin or quote.created_by_id == request.user.id):
        return Response({'detail': '该报价单为只读（他人分享）'}, status=status.HTTP_403_FORBIDDEN)
    if quote.status != 'DRAFT':
        return Response({'detail': '只有草稿报价单可以新增明细'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = AddItemFromProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    from products.models import Product
    try:
        product = Product.objects.get(pk=serializer.validated_data['product_id'], is_active=True)
    except Product.DoesNotExist:
        return Response({'detail': '产品不存在或已下架'}, status=status.HTTP_404_NOT_FOUND)

    item = QuoteService.add_item_from_product(
        quote=quote, product=product,
        selections=serializer.validated_data.get('selections', {}),
        image_id=serializer.validated_data.get('image_id'),
        quantity=serializer.validated_data.get('quantity', 1),
    )
    return Response(QuoteItemSerializer(item).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_item_from_product_view(request, pk):
    """PATCH /api/quotes/items/{id}/from-product/ — 原位更新配置和价格。"""
    if not has_module_permission(request.user, 'QUOTE', 'update'):
        return Response({'detail': '缺少报价修改权限'}, status=status.HTTP_403_FORBIDDEN)
    try:
        item = QuoteItem.objects.select_related('quote').get(pk=pk)
    except QuoteItem.DoesNotExist:
        return Response({'detail': '报价明细不存在'}, status=status.HTTP_404_NOT_FOUND)
    if not (request.user.is_admin or item.quote.created_by_id == request.user.id):
        return Response({'detail': '该报价单为只读（他人分享）'}, status=status.HTTP_403_FORBIDDEN)
    if item.quote.status != 'DRAFT':
        return Response({'detail': '只有草稿报价单可以修改明细'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = AddItemFromProductSerializer(data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    from products.models import Product
    product_id = serializer.validated_data.get('product_id') or item.product_id
    try:
        product = Product.objects.get(pk=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({'detail': '产品不存在或已下架'}, status=status.HTTP_404_NOT_FOUND)
    updated = QuoteService.update_item_from_product(
        item=item, product=product,
        selections=serializer.validated_data.get('selections', item.config_attributes),
        image_id=serializer.validated_data.get('image_id') if 'image_id' in serializer.validated_data else None,
        quantity=serializer.validated_data.get('quantity'),
    )
    return Response(QuoteItemSerializer(updated).data)
