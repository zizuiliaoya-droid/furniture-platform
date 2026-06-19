"""Document serializers."""
from rest_framework import serializers
from .models import Document, DocumentFolder


class DocumentFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFolder
        fields = ['id', 'name', 'doc_type', 'parent', 'sort_order']


class DocumentFolderTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = DocumentFolder
        fields = ['id', 'name', 'doc_type', 'parent', 'sort_order', 'children', 'document_count']

    def get_children(self, obj):
        return DocumentFolderTreeSerializer(obj.children.all().order_by('sort_order', 'id'), many=True).data

    def get_document_count(self, obj):
        return obj.documents.count()


class DocumentSerializer(serializers.ModelSerializer):
    folder_name = serializers.CharField(source='folder.name', read_only=True, default=None)

    class Meta:
        model = Document
        fields = [
            'id', 'name', 'doc_type', 'resource_type', 'content',
            'folder', 'folder_name',
            'file_path', 'file_size', 'mime_type', 'tags',
            'created_by', 'created_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class DocumentTagUpdateSerializer(serializers.Serializer):
    tags = serializers.ListField(child=serializers.CharField())


class RichTextDocumentCreateSerializer(serializers.Serializer):
    """富文本文档创建（培训资料等）"""
    name = serializers.CharField(max_length=300)
    doc_type = serializers.ChoiceField(choices=DocumentFolder.DOC_TYPE_CHOICES, default='TRAINING')
    folder = serializers.IntegerField(required=False, allow_null=True)
    content = serializers.CharField(allow_blank=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)
