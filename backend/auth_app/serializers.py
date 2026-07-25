"""User serializers."""
from rest_framework import serializers
from .models import Department, User


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'parent', 'sort_order']


class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'role', 'department',
                  'is_active', 'is_admin', 'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined', 'is_admin']

    def validate(self, attrs):
        request = self.context.get('request')
        actor = getattr(request, 'user', None)
        instance = self.instance
        if instance and 'is_active' in self.initial_data:
            raise serializers.ValidationError({'is_active': '请使用专用的用户状态切换接口'})
        requested_role = attrs.get('role', instance.role if instance else 'STAFF')
        if requested_role == 'SUPER_ADMIN' and getattr(actor, 'role', None) != 'SUPER_ADMIN':
            raise serializers.ValidationError({'role': '只有超级管理员可以授予超级管理员角色'})
        if instance and instance.role == 'SUPER_ADMIN' and getattr(actor, 'role', None) != 'SUPER_ADMIN':
            raise serializers.ValidationError('只有超级管理员可以修改超级管理员账号')
        if instance and actor and instance.pk == actor.pk and requested_role != instance.role:
            raise serializers.ValidationError({'role': '不能修改自己的角色'})
        if instance and instance.role == 'SUPER_ADMIN':
            removing_last = requested_role != 'SUPER_ADMIN' or attrs.get('is_active') is False
            if removing_last and User.objects.filter(role='SUPER_ADMIN', is_active=True).exclude(pk=instance.pk).count() == 0:
                raise serializers.ValidationError('系统必须至少保留一个启用的超级管理员')
        return attrs


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'display_name', 'role', 'department']

    def validate_role(self, value):
        request = self.context.get('request')
        if value == 'SUPER_ADMIN' and getattr(getattr(request, 'user', None), 'role', None) != 'SUPER_ADMIN':
            raise serializers.ValidationError('只有超级管理员可以创建超级管理员账号')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6)
