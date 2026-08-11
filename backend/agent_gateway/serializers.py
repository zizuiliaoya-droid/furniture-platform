"""Serializers shared by Agent Gateway endpoints."""
from rest_framework import serializers


class CapabilitySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    method = serializers.CharField()
    path = serializers.CharField()
    mode = serializers.ChoiceField(choices=['read', 'draft', 'write'])
    required_permission = serializers.CharField(allow_blank=True)
    requires_confirmation = serializers.BooleanField()
