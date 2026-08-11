"""Authentication and user management views."""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Department, RolePermission, User
from .permissions import IsAdminRole
from .serializers import (
    DepartmentSerializer, LoginSerializer, ResetPasswordSerializer,
    UserCreateSerializer, UserSerializer,
)
from .services import AuthService, PermissionMatrixService
from common.throttles import LoginRateThrottle


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        result = AuthService.login(**serializer.validated_data)
    except ValueError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        'token': result['token'],
        'user': UserSerializer(result['user']).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    AuthService.logout(request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    data = UserSerializer(request.user).data
    data['permissions'] = PermissionMatrixService.effective_for(request.user)
    return Response(data)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated, IsAdminRole])
def permission_matrix_view(request):
    """AUTH-3 角色权限矩阵：GET 读取完整矩阵；PUT 批量更新。"""
    if request.method == 'GET':
        return Response(PermissionMatrixService.get_matrix())
    items = request.data.get('items', [])
    PermissionMatrixService.update_matrix(items)
    return Response(PermissionMatrixService.get_matrix())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_permissions_view(request):
    """当前用户的有效权限（前端菜单/按钮控制用）。"""
    return Response({
        'role': request.user.role,
        'is_admin': request.user.is_admin,
        'permissions': PermissionMatrixService.effective_for(request.user),
    })


class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all().order_by('sort_order', 'id')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def perform_update(self, serializer):
        serializer.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def toggle_user_status(request, pk):
    try:
        target = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    if target.role == 'SUPER_ADMIN' and request.user.role != 'SUPER_ADMIN':
        return Response({'detail': '只有超级管理员可以修改超级管理员账号'}, status=status.HTTP_403_FORBIDDEN)
    if target.pk == request.user.pk and target.is_active:
        return Response({'detail': '不能停用自己的账号'}, status=status.HTTP_400_BAD_REQUEST)
    if target.role == 'SUPER_ADMIN' and target.is_active and not User.objects.filter(
            role='SUPER_ADMIN', is_active=True).exclude(pk=target.pk).exists():
        return Response({'detail': '系统必须至少保留一个启用的超级管理员'}, status=status.HTTP_400_BAD_REQUEST)
    user = AuthService.toggle_status(pk)
    return Response(UserSerializer(user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def reset_user_password(request, pk):
    try:
        target = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    if target.role == 'SUPER_ADMIN' and request.user.role != 'SUPER_ADMIN':
        return Response({'detail': '只有超级管理员可以重置超级管理员密码'}, status=status.HTTP_403_FORBIDDEN)
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    AuthService.reset_password(pk, serializer.validated_data['new_password'])
    return Response({'detail': '密码重置成功'})
