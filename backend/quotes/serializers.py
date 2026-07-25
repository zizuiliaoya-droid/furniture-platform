"""Quote serializers."""
from rest_framework import serializers
from .models import Quote, QuoteItem, QuoteShare


class QuoteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteItem
        fields = [
            'id', 'product', 'product_name', 'config_name',
            'config_attributes', 'image', 'image_url',
            'unit_price', 'quantity', 'discount', 'subtotal', 'sort_order',
        ]
        read_only_fields = ['id', 'discount', 'subtotal']


class QuoteListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.display_name', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Quote
        fields = [
            'id', 'title', 'customer_name', 'status',
            'total_amount', 'item_count', 'created_by_name',
            'created_at', 'updated_at',
        ]

    def get_item_count(self, obj):
        return obj.items.count()


class QuoteDetailSerializer(serializers.ModelSerializer):
    items = QuoteItemSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.display_name', read_only=True)

    class Meta:
        model = Quote
        fields = [
            'id', 'title', 'customer_name', 'status', 'notes', 'terms', 'discount',
            'total_amount', 'items', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'total_amount', 'created_by', 'created_at', 'updated_at']


class QuoteCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = ['title', 'customer_name', 'status', 'notes', 'terms', 'discount']


class AddItemFromProductSerializer(serializers.Serializer):
    """从产品创建或更新报价明细。"""
    product_id = serializers.IntegerField()
    selections = serializers.DictField(child=serializers.CharField(), required=False, default=dict)
    image_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(required=False, default=1, min_value=1)



class QuoteShareSerializer(serializers.ModelSerializer):
    shared_with_name = serializers.CharField(source='shared_with.display_name', read_only=True)
    shared_with_username = serializers.CharField(source='shared_with.username', read_only=True)

    class Meta:
        model = QuoteShare
        fields = ['id', 'quote', 'shared_with', 'shared_with_name', 'shared_with_username', 'created_at']
        read_only_fields = ['id', 'quote', 'created_at']
