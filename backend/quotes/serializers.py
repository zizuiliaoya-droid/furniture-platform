"""Quote serializers."""
from rest_framework import serializers
from .models import Quote, QuoteItem


class QuoteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteItem
        fields = [
            'id', 'product', 'product_name', 'config_name',
            'unit_price', 'quantity', 'discount', 'subtotal', 'sort_order',
        ]
        read_only_fields = ['id', 'subtotal']


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
            'id', 'title', 'customer_name', 'status', 'notes', 'terms',
            'total_amount', 'items', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'total_amount', 'created_by', 'created_at', 'updated_at']


class QuoteCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = ['title', 'customer_name', 'status', 'notes', 'terms']
