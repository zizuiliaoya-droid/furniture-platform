"""Sharing views."""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from auth_app.permissions import has_module_permission

from .models import ShareLink
from .serializers import (
    ClickTrackSerializer, ShareLinkCreateSerializer,
    ShareLinkSerializer, ShareVerifySerializer,
)
from .services import ShareService


class ShareLinkViewSet(ModelViewSet):
    serializer_class = ShareLinkSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    CONTENT_MODULE = {
        'PRODUCT': 'PRODUCT', 'CASE': 'CASE', 'QUOTE': 'QUOTE',
        'CATALOG': 'CATALOG', 'BATCH': 'CATALOG',
    }

    def _assert_share_permission(self, content_type):
        module = self.CONTENT_MODULE.get(content_type)
        if not module or not has_module_permission(self.request.user, module, 'share'):
            raise PermissionDenied('缺少对应模块的分享权限')

    def get_queryset(self):
        allowed_types = [
            content_type for content_type, module in self.CONTENT_MODULE.items()
            if has_module_permission(self.request.user, module, 'share')
        ]
        return ShareLink.objects.filter(created_by=self.request.user, content_type__in=allowed_types)

    def create(self, request, *args, **kwargs):
        serializer = ShareLinkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._assert_share_permission(serializer.validated_data['content_type'])
        link = ShareService.create_link(serializer.validated_data, request.user)
        return Response(ShareLinkSerializer(link).data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self._assert_share_permission(instance.content_type)
        instance.delete()


@api_view(['GET'])
@permission_classes([AllowAny])
def share_content_view(request, token):
    try:
        share = ShareLink.objects.get(token=token)
    except ShareLink.DoesNotExist:
        return Response({'detail': '链接不存在'}, status=status.HTTP_404_NOT_FOUND)
    error = ShareService.validate_access(share)
    if error:
        return Response({'detail': error}, status=status.HTTP_403_FORBIDDEN)
    if share.password_hash:
        return Response({
            'requires_password': True,
            'title': share.title,
            'content_type': share.content_type,
        })
    ShareService.log_access(share, request)
    content = ShareService.get_shared_content(share)
    branding = ShareService.get_branding()
    return Response({'title': share.title, 'branding': branding, **content})


@api_view(['POST'])
@permission_classes([AllowAny])
def share_verify_view(request, token):
    try:
        share = ShareLink.objects.get(token=token)
    except ShareLink.DoesNotExist:
        return Response({'detail': '链接不存在'}, status=status.HTTP_404_NOT_FOUND)
    error = ShareService.validate_access(share)
    if error:
        return Response({'detail': error}, status=status.HTTP_403_FORBIDDEN)
    serializer = ShareVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if not ShareService.verify_password(share, serializer.validated_data['password']):
        return Response({'detail': '密码错误'}, status=status.HTTP_400_BAD_REQUEST)
    ShareService.log_access(share, request)
    content = ShareService.get_shared_content(share)
    branding = ShareService.get_branding()
    return Response({'title': share.title, 'branding': branding, **content})


@api_view(['POST'])
@permission_classes([AllowAny])
def share_track_click(request, token):
    try:
        share = ShareLink.objects.get(token=token)
    except ShareLink.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = ClickTrackSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    ShareService.track_click(share, serializer.validated_data, request)
    return Response(status=status.HTTP_201_CREATED)
