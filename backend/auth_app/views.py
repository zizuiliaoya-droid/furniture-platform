"""Authentication and user management views."""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import RolePermission, User
from .permissions import IsAdminRole
from .serializers import (
    LoginSerializer, ResetPasswordSerializer,
    UserCreateSerializer, UserSerializer,
)
from .services import AuthService, PermissionMatrixService


@api_view(['POST'])
@permission_classes([AllowAny])
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
        user = AuthService.toggle_status(pk)
    except User.DoesNotExist:
        return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    return Response(UserSerializer(user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def reset_user_password(request, pk):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        AuthService.reset_password(pk, serializer.validated_data['new_password'])
    except User.DoesNotExist:
        return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'detail': '密码重置成功'})
