"""Serializers shared by Agent Gateway endpoints."""
from rest_framework import serializers

from products.models import Product
from products.serializers import (
    ProductConfigDimensionSerializer,
    ProductConfigPresetSerializer,
    ProductImageSerializer,
)


class CapabilitySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    method = serializers.CharField()
    path = serializers.CharField()
    mode = serializers.ChoiceField(choices=['read', 'draft', 'write'])
    required_permission = serializers.CharField(allow_blank=True)
    requires_confirmation = serializers.BooleanField()


class AgentProductSearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True, max_length=200, default='')
    category_l1 = serializers.CharField(required=False, max_length=30)
    category_l2 = serializers.CharField(required=False, max_length=50)
    brand = serializers.IntegerField(required=False, min_value=1)
    origin = serializers.ChoiceField(required=False, choices=Product.ORIGIN_CHOICES)
    lead_time = serializers.CharField(required=False, max_length=50)
    min_price = serializers.DecimalField(required=False, max_digits=12, decimal_places=2)
    max_price = serializers.DecimalField(required=False, max_digits=12, decimal_places=2)
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=20, default=10)

    def validate(self, attrs):
        if (
            attrs.get('min_price') is not None
            and attrs.get('max_price') is not None
            and attrs['min_price'] > attrs['max_price']
        ):
            raise serializers.ValidationError('最低价格不能大于最高价格')
        return attrs


class AgentProductSummarySerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True, default='')
    cover_image = serializers.SerializerMethodField()
    web_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'category_l1', 'category_l2',
            'brand_name', 'origin', 'lead_time', 'min_price',
            'pricing_mode', 'cover_image', 'web_url',
        ]

    def get_cover_image(self, obj):
        image = next((item for item in obj.images.all() if item.is_cover), None)
        image = image or next(iter(obj.images.all()), None)
        return image.image_path if image else ''

    def get_web_url(self, obj):
        return f'{self.context["web_url"]}/products/{obj.id}'


class AgentProductDetailSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True, default='')
    images = ProductImageSerializer(many=True, read_only=True)
    config_dimensions = ProductConfigDimensionSerializer(many=True, read_only=True)
    config_presets = ProductConfigPresetSerializer(many=True, read_only=True)
    web_url = serializers.SerializerMethodField()
    edit_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'description', 'category_l1', 'category_l2',
            'brand', 'brand_name', 'origin', 'lead_time', 'pricing_mode',
            'base_price', 'min_price', 'shape', 'length_mm', 'width_mm',
            'height_mm', 'diameter_mm', 'official_url', 'material_album',
            'model_3d_url', 'images', 'config_dimensions', 'config_presets',
            'web_url', 'edit_url',
        ]

    def get_web_url(self, obj):
        return f'{self.context["web_url"]}/products/{obj.id}'

    def get_edit_url(self, obj):
        return f'{self.context["web_url"]}/products/{obj.id}/edit'


class AgentContentSearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True, max_length=200, default='')
    doc_type = serializers.ChoiceField(
        required=False,
        choices=['DESIGN', 'TRAINING', 'CERTIFICATE'],
    )
    industry = serializers.CharField(required=False, max_length=30)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=20, default=10)
