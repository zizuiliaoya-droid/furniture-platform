"""Create initial admin user from environment variables."""
import os
import sys

# Ensure the backend directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from auth_app.models import User

username = os.environ.get('ADMIN_USERNAME', 'admin')
password = os.environ.get('ADMIN_PASSWORD', 'admin123456')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        password=password,
        role='ADMIN',
        display_name='系统管理员',
    )
    print(f'Admin user "{username}" created.')
else:
    print(f'Admin user "{username}" already exists, skipping.')
