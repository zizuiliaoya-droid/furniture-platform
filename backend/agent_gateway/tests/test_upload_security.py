import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.test import override_settings
from rest_framework.test import APIClient

from common.file_storage import FileStorageService
from common.views import media_view
from documents.models import Document


def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.mark.django_db
def test_active_html_document_upload_is_rejected(admin_user):
    response = authenticated_client(admin_user).post(
        '/api/documents/upload/',
        {
            'doc_type': 'DESIGN',
            'file': SimpleUploadedFile(
                'payload.html',
                b'<script>window.top.location="https://attacker.invalid"</script>',
                content_type='text/html',
            ),
        },
        format='multipart',
    )

    assert response.status_code == 400
    assert Document.objects.count() == 0


@pytest.mark.django_db
def test_generic_document_create_route_is_disabled(admin_user):
    response = authenticated_client(admin_user).post(
        '/api/documents/',
        {'name': 'unsafe', 'file_path': '../../outside.html'},
        format='json',
    )

    assert response.status_code == 405


def test_fake_image_content_is_rejected():
    upload = SimpleUploadedFile(
        'fake.jpg', b'<script>alert(1)</script>', content_type='image/jpeg')

    with pytest.raises(ValueError, match='内容无效'):
        FileStorageService.validate_image(upload)


def test_media_response_is_sandboxed(tmp_path):
    media_file = tmp_path / 'legacy.html'
    media_file.write_text('<script>alert(1)</script>', encoding='utf-8')

    response = media_view(
        RequestFactory().get('/media/legacy.html'),
        'legacy.html',
        document_root=tmp_path,
    )

    assert response.status_code == 200
    assert response['X-Content-Type-Options'] == 'nosniff'
    assert response['Content-Security-Policy'] == "default-src 'none'; sandbox"


def test_media_delete_cannot_escape_root(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        with pytest.raises(ValueError, match='超出媒体目录'):
            FileStorageService.delete('../outside.txt')
