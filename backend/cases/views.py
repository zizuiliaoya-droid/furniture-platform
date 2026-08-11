"""Case views."""
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from auth_app.permissions import HasModulePermission, require_module_permission
from common.file_storage import FileStorageService
from .models import Case, CaseImage
from .serializers import CaseDetailSerializer, CaseImageSerializer, CaseListSerializer


class CaseViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'CASE'
    permission_action_map = {'upload_images': 'update'}

    def get_queryset(self):
        qs = Case.objects.select_related('created_by').prefetch_related('images', 'products')
        industry = self.request.query_params.get('industry')
        if industry:
            qs = qs.filter(industry=industry)
        product_id = self.request.query_params.get('product_id')
        if product_id:
            qs = qs.filter(products__id=product_id)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return CaseListSerializer
        return CaseDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        case = self.get_object()
        files = request.FILES.getlist('images')
        created = []
        for f in files:
            if f.size > settings.MAX_IMAGE_SIZE:
                return Response(
                    {'detail': f'图片 {f.name} 超过大小限制'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                FileStorageService.validate_image(f)
            except ValueError as exc:
                return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            path = FileStorageService.upload(f, 'cases')
            thumbs = FileStorageService.generate_thumbnails(path)
            img = CaseImage.objects.create(
                case=case, image_path=path, thumbnail_path=thumbs,
                sort_order=case.images.count(),
            )
            created.append(img)
        return Response(CaseImageSerializer(created, many=True).data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@require_module_permission('CASE', 'update')
def delete_case_image(request, pk):
    try:
        image = CaseImage.objects.get(pk=pk)
    except CaseImage.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    FileStorageService.delete_with_thumbnails(image.image_path)
    image.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
