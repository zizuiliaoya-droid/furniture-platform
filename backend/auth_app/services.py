"""Authentication service."""
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from .models import User


class AuthService:
    @staticmethod
    def login(username: str, password: str) -> dict:
        user = User.objects.filter(username=username).first()
        if not user:
            raise ValueError('用户名或密码错误')
        if not user.is_active:
            raise ValueError('账号已被禁用，请联系管理员')
        if not user.check_password(password):
            raise ValueError('用户名或密码错误')
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        return {'token': token.key, 'user': user}

    @staticmethod
    def logout(user) -> None:
        Token.objects.filter(user=user).delete()

    @staticmethod
    def toggle_status(user_id: int) -> User:
        user = User.objects.get(pk=user_id)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        if not user.is_active:
            Token.objects.filter(user=user).delete()
        return user

    @staticmethod
    def reset_password(user_id: int, new_password: str) -> None:
        user = User.objects.get(pk=user_id)
        user.set_password(new_password)
        user.save()
        Token.objects.filter(user=user).delete()
