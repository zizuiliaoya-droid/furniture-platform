"""Agent 文档和案例检索工具测试。"""
import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from cases.models import Case
from documents.models import Document


def agent_client(user, skill):
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Token {token.key}',
        HTTP_X_AGENT_SKILL=skill,
    )
    return client


@pytest.mark.django_db
def test_document_search_returns_bounded_content_and_deep_link(admin_user, settings):
    settings.PUBLIC_WEB_URL = 'https://furniture.example.com'
    document = Document.objects.create(
        name='人体工学培训手册',
        doc_type='TRAINING',
        resource_type='RICH_TEXT',
        content='坐姿与人体工学。' * 100,
        tags=['培训', '座椅'],
        created_by=admin_user,
    )
    client = agent_client(admin_user, 'furniture-documents')

    response = client.get('/api/agent/documents/search/', {'q': '人体工学'})

    assert response.status_code == 200
    item = response.data['items'][0]
    assert item['id'] == document.id
    assert len(item['content_excerpt']) <= 501
    assert item['web_url'] == 'https://furniture.example.com/documents/training'


@pytest.mark.django_db
def test_case_search_returns_related_product_ids(
    admin_user,
    product_matrix,
    settings,
):
    settings.PUBLIC_WEB_URL = 'https://furniture.example.com'
    case = Case.objects.create(
        title='科技公司总部项目',
        description='人体工学座椅与升降桌方案',
        industry='TECH_OFFICE',
        created_by=admin_user,
    )
    case.products.add(product_matrix)
    client = agent_client(admin_user, 'furniture-documents')

    response = client.get('/api/agent/cases/search/', {'q': '升降桌'})

    assert response.status_code == 200
    item = response.data['items'][0]
    assert item['id'] == case.id
    assert item['related_product_ids'] == [product_matrix.id]
    assert item['web_url'] == f'https://furniture.example.com/cases/{case.id}'
