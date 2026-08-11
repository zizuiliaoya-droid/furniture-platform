"""File storage service for uploads, deletions, and thumbnail generation."""
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.utils.text import get_valid_filename
from PIL import Image


class FileStorageService:
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    IMAGE_FORMATS = {'JPEG', 'PNG', 'WEBP', 'GIF'}
    DOCUMENT_EXTENSIONS = {
        '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
        '.txt', '.mp3', '.wav', '.m4a', '.ogg', '.mp4', '.webm',
    }

    @staticmethod
    def _media_root() -> Path:
        return Path(settings.MEDIA_ROOT).resolve()

    @staticmethod
    def _resolve(file_path: str) -> Path:
        root = FileStorageService._media_root()
        candidate = (root / str(file_path)).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError('文件路径超出媒体目录') from exc
        return candidate

    @staticmethod
    def validate_image(file) -> None:
        extension = Path(file.name).suffix.lower()
        if extension not in FileStorageService.IMAGE_EXTENSIONS:
            raise ValueError(f'图片 {file.name} 格式不受支持')
        position = file.tell()
        try:
            image = Image.open(file)
            image_format = image.format
            image.verify()
        except Exception as exc:
            raise ValueError(f'图片 {file.name} 内容无效') from exc
        finally:
            file.seek(position)
        if image_format not in FileStorageService.IMAGE_FORMATS:
            raise ValueError(f'图片 {file.name} 内容格式不受支持')

    @staticmethod
    def validate_document(file) -> None:
        extension = Path(file.name).suffix.lower()
        if extension not in FileStorageService.DOCUMENT_EXTENSIONS:
            raise ValueError('仅支持 PDF、Office、文本、音频和视频文件')
        position = file.tell()
        header = file.read(16)
        file.seek(position)
        if extension == '.pdf' and not header.startswith(b'%PDF-'):
            raise ValueError('PDF 文件内容无效')
        if extension in {'.docx', '.pptx', '.xlsx'} and not header.startswith(b'PK'):
            raise ValueError('Office 文件内容无效')
        if extension in {'.doc', '.ppt', '.xls'} and not header.startswith(b'\xd0\xcf\x11\xe0'):
            raise ValueError('Office 文件内容无效')

    @staticmethod
    def upload(file, subdirectory: str) -> str:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', subdirectory):
            raise ValueError('非法的上传目录')
        date_dir = datetime.now().strftime('%Y%m%d')
        safe_name = get_valid_filename(Path(file.name).name)
        if not safe_name:
            raise ValueError('文件名无效')
        filename = f"{uuid.uuid4().hex[:12]}_{safe_name}"
        relative_path = os.path.join(subdirectory, date_dir, filename)
        full_path = FileStorageService._resolve(relative_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)
        return relative_path

    @staticmethod
    def delete(file_path: str) -> None:
        if not file_path:
            return
        full_path = FileStorageService._resolve(file_path)
        if full_path.exists():
            full_path.unlink()

    @staticmethod
    def generate_thumbnails(image_path: str) -> dict:
        full_path = FileStorageService._resolve(image_path)
        if not full_path.exists():
            return {}
        thumbnails = {}
        try:
            img = Image.open(full_path)
            for name, size in settings.THUMBNAIL_SIZES.items():
                thumb = img.copy()
                thumb.thumbnail(size, Image.Resampling.LANCZOS)
                base, ext = os.path.splitext(image_path)
                thumb_path = f"{base}_{name}{ext}"
                thumb_full = FileStorageService._resolve(thumb_path)
                thumb_full.parent.mkdir(parents=True, exist_ok=True)
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
