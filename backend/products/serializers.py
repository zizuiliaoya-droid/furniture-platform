"""Product serializers."""
from rest_framework import serializers
from .models import (
    Brand, Category, Product, ProductCategory, ProductConfig,
    ProductConfigDimension, ProductConfigPreset, ProductDocument, ProductImage,
    ProductPriceMatrix, ProductPriceRule,
)


# ─── Brand ───────────────────────────────────────────────────────────────────

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'is_self_owned', 'sort_order', 'created_at']
        read_only_fields = ['id', 'created_at']


# ─── Category（过渡保留） ─────────────────────────────────────────────────────

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'dimension', 'sort_order']


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'dimension', 'sort_order', 'children']

    def get_children(self, obj):
        children = obj.children.all().order_by('sort_order', 'id')
        return CategoryTreeSerializer(children, many=True).data


# ─── ProductImage ─────────────────────────────────────────────────────────────

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_path', 'thumbnail_path', 'sort_order', 'is_cover']


# ─── ProductConfig（旧，兼容保留） ────────────────────────────────────────────

class ProductConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductConfig
        fields = ['id', 'config_name', 'attributes', 'guide_price', 'created_at']


# ─── ProductConfigDimension ───────────────────────────────────────────────────

class ProductConfigDimensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductConfigDimension
        fields = [
            'id', 'dimension_key', 'dimension_label', 'options',
            'parent_dimension', 'is_required', 'sort_order',
        ]


class ProductConfigDimensionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductConfigDimension
        fields = [
            'dimension_key', 'dimension_label', 'options',
            'parent_dimension', 'is_required', 'sort_order',
        ]


# ─── ProductConfigPreset（预设/默认配置） ─────────────────────────────────────

class ProductConfigPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductConfigPreset
        fields = ['id', 'code', 'label', 'selections', 'is_default', 'sort_order']


# ─── ProductPriceMatrix ───────────────────────────────────────────────────────

class ProductPriceMatrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPriceMatrix
        fields = ['id', 'config_signature', 'config_attributes', 'price']


# ─── ProductPriceRule ─────────────────────────────────────────────────────────

class ProductPriceRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPriceRule
        fields = ['id', 'dimension_key', 'option_key', 'price_delta', 'sort_order']


# ─── ProductDocument ──────────────────────────────────────────────────────────

class ProductDocumentSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source='document.name', read_only=True)
    file_path = serializers.CharField(source='document.file_path', read_only=True)
    mime_type = serializers.CharField(source='document.mime_type', read_only=True)
    file_size = serializers.IntegerField(source='document.file_size', read_only=True)

    class Meta:
        model = ProductDocument
        fields = [
            'id', 'document', 'document_name', 'file_path', 'mime_type',
            'file_size', 'relation_type', 'sort_order', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ProductDocumentCreateSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    relation_type = serializers.ChoiceField(choices=ProductDocument.RELATION_TYPE_CHOICES)


# ─── Product List ─────────────────────────────────────────────────────────────

class ProductListSerializer(serializers.ModelSerializer):
    cover_image = serializers.SerializerMethodField()
    brand_name = serializers.CharField(source='brand.name', read_only=True, default='')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'category_l1', 'category_l2',
            'brand', 'brand_name', 'origin', 'lead_time',
            'min_price', 'is_active', 'cover_image', 'created_at',
        ]

    def get_cover_image(self, obj):
        cover = obj.images.filter(is_cover=True).first()
        if not cover:
            cover = obj.images.first()
        return ProductImageSerializer(cover).data if cover else None


# ─── Product Detail ───────────────────────────────────────────────────────────

class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    configs = ProductConfigSerializer(many=True, read_only=True)
    config_dimensions = ProductConfigDimensionSerializer(many=True, read_only=True)
    config_presets = ProductConfigPresetSerializer(many=True, read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, default='')
    created_by_name = serializers.CharField(source='created_by.display_name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'description',
            'category_l1', 'category_l2', 'brand', 'brand_name',
            'origin', 'lead_time', 'pricing_mode', 'base_price', 'min_price',
            'shape', 'length_mm', 'width_mm', 'height_mm', 'diameter_mm',
            'official_url', 'material_album', 'model_3d_url',
            'is_active', 'images', 'configs', 'config_dimensions', 'config_presets',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


# ─── Product Create/Update ────────────────────────────────────────────────────

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'code', 'description',
            'category_l1', 'category_l2', 'brand', 'origin', 'lead_time',
            'pricing_mode', 'base_price', 'min_price',
            'shape', 'length_mm', 'width_mm', 'height_mm', 'diameter_mm',
            'official_url', 'material_album', 'model_3d_url',
            'is_active',
        ]

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProductCompositeCreateSerializer(serializers.Serializer):
    """同一事务创建产品、配置维度、默认组合和价格矩阵。图片通过 multipart 单独传入。"""
    product = ProductCreateUpdateSerializer()
    dimensions = ProductConfigDimensionWriteSerializer(many=True, required=False, default=list)
    presets = ProductConfigPresetSerializer(many=True, required=False, default=list)
    price_matrix = serializers.ListField(child=serializers.DictField(), required=False, default=list)

    def validate(self, attrs):
        dimensions = attrs.get('dimensions', [])
        keys = [d['dimension_key'] for d in dimensions]
        if len(keys) != len(set(keys)):
            raise serializers.ValidationError({'dimensions': '配置维度键不能重复'})
        defaults = [p for p in attrs.get('presets', []) if p.get('is_default')]
        if len(defaults) > 1:
            raise serializers.ValidationError({'presets': '每个产品最多一个默认配置'})
        return attrs


# ─── Calculate Price Request ──────────────────────────────────────────────────

class CalculatePriceSerializer(serializers.Serializer):
    selections = serializers.DictField(child=serializers.CharField())
