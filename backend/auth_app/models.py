"""User model extending AbstractUser with role and display_name."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', '管理员'),
        ('STAFF', '普通员工'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STAFF')
    display_name = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.display_name or self.username
