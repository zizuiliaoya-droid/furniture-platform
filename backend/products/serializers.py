"""Product serializers."""
from rest_framework import serializers
from .models import Category, Product, ProductConfig, ProductImage


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


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_path', 'thumbnail_path', 'sort_order', 'is_cover']


class ProductConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductConfig
        fields = ['id', 'config_name', 'attributes', 'guide_price', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    cover_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'origin', 'min_price',
            'is_active', 'category', 'category_name',
            'cover_image', 'created_at',
        ]

    def get_cover_image(self, obj):
        cover = obj.images.filter(is_cover=True).first()
        if not cover:
            cover = obj.images.first()
        return ProductImageSerializer(cover).data if cover else None


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    configs = ProductConfigSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        source='categories', queryset=Category.objects.all(), many=True, required=False
    )
    created_by_name = serializers.CharField(source='created_by.display_name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'description', 'origin', 'min_price',
            'is_active', 'category', 'category_name', 'category_ids',
            'images', 'configs', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False, write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'name', 'code', 'description', 'origin', 'min_price',
            'is_active', 'category', 'category_ids',
        ]

    def create(self, validated_data):
        category_ids = validated_data.pop('category_ids', [])
        product = Product.objects.create(**validated_data)
        if category_ids:
            product.categories.set(category_ids)
        return product

    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if category_ids is not None:
            instance.categories.set(category_ids)
        return instance
