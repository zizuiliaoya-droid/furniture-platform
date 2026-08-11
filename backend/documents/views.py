"""Document views."""
import os

from django.conf import settings
from django.http import FileResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from auth_app.permissions import HasModulePermission, require_module_permission
from common.file_storage import FileStorageService
from .models import Document, DocumentFolder
from .serializers import (
    DocumentFolderSerializer, DocumentFolderTreeSerializer,
    DocumentSerializer, DocumentTagUpdateSerializer,
    RichTextDocumentCreateSerializer,
)


class DocumentFolderViewSet(ModelViewSet):
    queryset = DocumentFolder.objects.all()
    serializer_class = DocumentFolderSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'DOCUMENT'

    def perform_destroy(self, instance):
        if instance.documents.exists() or instance.children.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError('文件夹非空，无法删除')
        instance.delete()

    def tree(self, request):
        doc_type = request.query_params.get('doc_type')
        qs = DocumentFolder.objects.filter(parent__isnull=True)
        if doc_type:
            qs = qs.filter(doc_type=doc_type)
        return Response(DocumentFolderTreeSerializer(qs.order_by('sort_order', 'id'), many=True).data)


class DocumentViewSet(ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'DOCUMENT'
    http_method_names = ['get', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = Document.objects.select_related('folder', 'created_by')
        doc_type = self.request.query_params.get('doc_type')
        if doc_type:
            qs = qs.filter(doc_type=doc_type)
        folder = self.request.query_params.get('folder')
        if folder:
            qs = qs.filter(folder_id=folder)
        tag = self.request.query_params.get('tag')
        if tag:
            qs = qs.filter(tags__contains=[tag])
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_module_permission('DOCUMENT', 'create')
def upload_document(request):
    file = request.FILES.get('file')
    if not file:
        return Response({'detail': '请选择文件'}, status=status.HTTP_400_BAD_REQUEST)
    if file.size > settings.MAX_DOCUMENT_SIZE:
        return Response({'detail': '文件大小不能超过 50MB'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        FileStorageService.validate_document(file)
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    doc_type = request.data.get('doc_type', 'DESIGN')
    folder_id = request.data.get('folder')
    path = FileStorageService.upload(file, 'documents')
    doc = Document.objects.create(
        name=file.name, doc_type=doc_type,
        folder_id=folder_id if folder_id else None,
        file_path=path, file_size=file.size,
        mime_type=file.content_type or 'application/octet-stream',
        created_by=request.user,
    )
    return Response(DocumentSerializer(doc).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@require_module_permission('DOCUMENT', 'view')
def download_document(request, pk):
    try:
        doc = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    full_path = os.path.join(settings.MEDIA_ROOT, doc.file_path)
    if not os.path.exists(full_path):
        return Response({'detail': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)
    response = FileResponse(open(full_path, 'rb'), content_type=doc.mime_type)
    response['Content-Disposition'] = f'attachment; filename="{doc.name}"'
    return response


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@require_module_permission('DOCUMENT', 'update')
def update_document_tags(request, pk):
    try:
        doc = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = DocumentTagUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    doc.tags = serializer.validated_data['tags']
    doc.save(update_fields=['tags'])
    return Response(DocumentSerializer(doc).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_module_permission('DOCUMENT', 'create')
def create_rich_text_document(request):
    """POST /api/documents/rich-text/ — 创建富文本文档（培训资料等）"""
    serializer = RichTextDocumentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    doc = Document.objects.create(
        name=data['name'],
        doc_type=data['doc_type'],
        resource_type='RICH_TEXT',
        content=data['content'],
        folder_id=data.get('folder'),
        file_path='',
        file_size=0,
        mime_type='text/html',
        tags=data.get('tags', []),
        created_by=request.user,
    )
    return Response(DocumentSerializer(doc).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@require_module_permission('DOCUMENT', 'update')
def update_rich_text_document(request, pk):
    """PATCH /api/documents/{id}/rich-text/ — 更新富文本内容"""
    try:
        doc = Document.objects.get(pk=pk, resource_type='RICH_TEXT')
    except Document.DoesNotExist:
        return Response({'detail': '富文本文档不存在'}, status=status.HTTP_404_NOT_FOUND)
    if 'name' in request.data:
        doc.name = request.data['name']
    if 'content' in request.data:
        doc.content = request.data['content']
    if 'tags' in request.data:
        doc.tags = request.data['tags']
    doc.save()
    return Response(DocumentSerializer(doc).data)
