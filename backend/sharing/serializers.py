"""Sharing serializers."""
from rest_framework import serializers
from .models import ShareLink


class ShareLinkSerializer(serializers.ModelSerializer):
    has_password = serializers.SerializerMethodField()

    class Meta:
        model = ShareLink
        fields = [
            'id', 'token', 'content_type', 'object_id', 'title',
            'has_password', 'expires_at', 'max_access_count',
            'access_count', 'is_active', 'created_by', 'created_at',
        ]
        read_only_fields = ['id', 'token', 'access_count', 'created_by', 'created_at']

    def get_has_password(self, obj):
        return bool(obj.password_hash)


class ShareLinkCreateSerializer(serializers.Serializer):
    content_type = serializers.ChoiceField(choices=['PRODUCT', 'CASE', 'QUOTE', 'CATALOG'])
    object_id = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(max_length=200)
    password = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    max_access_count = serializers.IntegerField(required=False, allow_null=True)


class ShareVerifySerializer(serializers.Serializer):
    password = serializers.CharField()


class ClickTrackSerializer(serializers.Serializer):
    event_type = serializers.CharField(max_length=20)
    object_id = serializers.IntegerField()
    object_name = serializers.CharField(max_length=200, required=False, default='')
