"""Quote views."""
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from auth_app.permissions import IsAdminRole
from .models import Quote, QuoteItem
from .serializers import (
    AddItemFromProductSerializer, QuoteCreateUpdateSerializer,
    QuoteDetailSerializer, QuoteItemSerializer, QuoteListSerializer,
)
from .services import QuoteService


class QuoteViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Quote.objects.select_related('created_by').prefetch_related('items')
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(customer_name__icontains=search))
        s = self.request.query_params.get('status')
        if s:
            qs = qs.filter(status=s)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return QuoteListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return QuoteCreateUpdateSerializer
        return QuoteDetailSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        new_status = serializer.validated_data.get('status')
        if new_status and new_status != serializer.instance.status:
            if not QuoteService.validate_status_change(serializer.instance.status, new_status):
                from rest_framework.exceptions import ValidationError
                raise ValidationError(f'不允许从 {serializer.instance.status} 变更为 {new_status}')
        serializer.save()

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        try:
            new_quote = QuoteService.duplicate(pk, request.user)
        except Quote.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(QuoteDetailSerializer(new_quote).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        try:
            pdf_bytes = QuoteService.export_pdf(pk)
        except Quote.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="quote_{pk}.pdf"'
        return response


class QuoteItemViewSet(ModelViewSet):
    serializer_class = QuoteItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = QuoteItem.objects.all()
        quote_pk = self.kwargs.get('quote_pk')
        if quote_pk:
            qs = qs.filter(quote_id=quote_pk)
        return qs

    def perform_create(self, serializer):
        item = serializer.save(quote_id=self.kwargs['quote_pk'])
        item.quote.recalculate_total()

    def perform_update(self, serializer):
        item = serializer.save()
        item.quote.recalculate_total()

    def perform_destroy(self, instance):
        quote = instance.quote
        instance.delete()
        quote.recalculate_total()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item_from_product_view(request, quote_pk):
    """POST /api/quotes/{id}/items/from-product/ — 一键加入报价单"""
    try:
        quote = Quote.objects.get(pk=quote_pk)
    except Quote.DoesNotExist:
        return Response({'detail': '报价单不存在'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AddItemFromProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    from products.models import Product
    try:
        product = Product.objects.get(pk=serializer.validated_data['product_id'])
    except Product.DoesNotExist:
        return Response({'detail': '产品不存在'}, status=status.HTTP_404_NOT_FOUND)

    item = QuoteService.add_item_from_product(
        quote=quote,
        product=product,
        selections=serializer.validated_data['selections'],
        image_id=serializer.validated_data.get('image_id'),
        quantity=serializer.validated_data.get('quantity', 1),
        discount=serializer.validated_data.get('discount', 0),
    )
    return Response(QuoteItemSerializer(item).data, status=status.HTTP_201_CREATED)
