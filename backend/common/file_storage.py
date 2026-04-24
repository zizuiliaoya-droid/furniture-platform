"""File storage service for uploads, deletions, and thumbnail generation."""
import os
import uuid
from datetime import datetime

from django.conf import settings
from PIL import Image


class FileStorageService:
    @staticmethod
    def upload(file, subdirectory: str) -> str:
        date_dir = datetime.now().strftime('%Y%m%d')
        filename = f"{uuid.uuid4().hex[:12]}_{file.name}"
        relative_path = os.path.join(subdirectory, date_dir, filename)
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)
        return relative_path

    @staticmethod
    def delete(file_path: str) -> None:
        if not file_path:
            return
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)

    @staticmethod
    def generate_thumbnails(image_path: str) -> dict:
        full_path = os.path.join(settings.MEDIA_ROOT, image_path)
        if not os.path.exists(full_path):
            return {}
        thumbnails = {}
        try:
            img = Image.open(full_path)
            for name, size in settings.THUMBNAIL_SIZES.items():
                thumb = img.copy()
                thumb.thumbnail(size, Image.Resampling.LANCZOS)
                base, ext = os.path.splitext(image_path)
                thumb_path = f"{base}_{name}{ext}"
                thumb_full = os.path.join(settings.MEDIA_ROOT, thumb_path)
                os.makedirs(os.path.dirname(thumb_full), exist_ok=True)
                thumb.save(thumb_full, quality=85)
                thumbnails[name] = thumb_path
        except Exception:
            pass
        return thumbnails

    @staticmethod
    def delete_with_thumbnails(image_path: str) -> None:
        FileStorageService.delete(image_path)
        if image_path:
            base, ext = os.path.splitext(image_path)
            for name in settings.THUMBNAIL_SIZES:
                FileStorageService.delete(f"{base}_{name}{ext}")
