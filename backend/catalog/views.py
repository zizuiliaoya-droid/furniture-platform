"""Catalog views - read-only product browsing."""
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

from products.models import Category, Product
from products.serializers import ProductListSerializer


class CatalogBrowseView(ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
        category = self.request.query_params.get('category')
        if category:
            cat = Category.objects.filter(pk=category).first()
            if cat:
                cat_ids = [cat.id] + list(cat.children.values_list('id', flat=True))
                qs = qs.filter(Q(category_id__in=cat_ids) | Q(categories__id__in=cat_ids)).distinct()
        return qs


class CatalogSearchView(ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
        q = self.request.query_params.get('q', '')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q)).distinct()
        return qs
