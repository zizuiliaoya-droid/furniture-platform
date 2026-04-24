"""Case serializers."""
from rest_framework import serializers
from products.models import Product
from products.serializers import ProductListSerializer
from .models import Case, CaseImage


class CaseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseImage
        fields = ['id', 'image_path', 'thumbnail_path', 'sort_order', 'is_cover']


class CaseListSerializer(serializers.ModelSerializer):
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = ['id', 'title', 'industry', 'cover_image', 'created_at']

    def get_cover_image(self, obj):
        cover = obj.images.filter(is_cover=True).first()
        if not cover:
            cover = obj.images.first()
        return CaseImageSerializer(cover).data if cover else None


class CaseDetailSerializer(serializers.ModelSerializer):
    images = CaseImageSerializer(many=True, read_only=True)
    related_products = ProductListSerializer(source='products', many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        source='products', queryset=Product.objects.all(),
        many=True, required=False, write_only=True,
    )

    class Meta:
        model = Case
        fields = [
            'id', 'title', 'description', 'industry',
            'images', 'related_products', 'product_ids',
            'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
