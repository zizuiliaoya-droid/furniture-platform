"""业务模块权限矩阵和跨模块聚合入口回归测试。"""
import pytest
from rest_framework.test import APIClient

from auth_app.models import RolePermission
from cases.models import Case
from documents.models import Document
from quotes.models import Quote


def client_for(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def allow(role, module, action):
    RolePermission.objects.update_or_create(
        role=role, module=module, action=action,
        defaults={'allowed': True},
    )


def deny(role, module, action):
    RolePermission.objects.update_or_create(
        role=role, module=module, action=action,
        defaults={'allowed': False},
    )


@pytest.mark.django_db
class TestBusinessModulePermissions:
    def test_catalog_requires_catalog_view(self, staff_user, product_matrix):
        client = client_for(staff_user)
        deny('STAFF', 'CATALOG', 'view')
        assert client.get('/api/catalog/').status_code == 403
        allow('STAFF', 'CATALOG', 'view')
        response = client.get('/api/catalog/')
        assert response.status_code == 200

    def test_case_create_uses_case_create_permission(self, staff_user):
        client = client_for(staff_user)
        payload = {'title': '权限案例', 'industry': 'OTHER'}
        deny('STAFF', 'CASE', 'create')
        assert client.post('/api/cases/', payload, format='json').status_code == 403
        allow('STAFF', 'CASE', 'create')
        response = client.post('/api/cases/', payload, format='json')
        assert response.status_code == 201, response.content

    def test_document_tags_require_update_permission(self, staff_user):
        document = Document.objects.create(
            name='权限文档', doc_type='DESIGN', resource_type='RICH_TEXT',
            content='正文', created_by=staff_user)
        client = client_for(staff_user)
        allow('STAFF', 'DOCUMENT', 'view')
        assert client.get('/api/documents/').status_code == 200
        assert client.patch(
            f'/api/documents/{document.id}/tags/', {'tags': ['A']}, format='json').status_code == 403
        allow('STAFF', 'DOCUMENT', 'update')
        response = client.patch(
            f'/api/documents/{document.id}/tags/', {'tags': ['A']}, format='json')
        assert response.status_code == 200, response.content

    def test_global_search_filters_each_module_and_foreign_quotes(
            self, staff_user, admin_user):
        Case.objects.create(
            title='Alpha案例', industry='OTHER', created_by=admin_user)
        Document.objects.create(
            name='Alpha文档', doc_type='DESIGN', resource_type='RICH_TEXT',
            content='正文', created_by=admin_user)
        Quote.objects.create(
            title='Alpha报价', customer_name='外部客户', created_by=admin_user)
        allow('STAFF', 'CASE', 'view')

        response = client_for(staff_user).get('/api/search/', {'q': 'Alpha'})
        assert response.status_code == 200
        assert len(response.data['cases']) == 1
        assert response.data['products'] == []
        assert response.data['documents'] == []
        assert response.data['quotes'] == []

    def test_dashboard_only_counts_visible_owned_quotes(
            self, staff_user, admin_user, product_matrix):
        own = Quote.objects.create(
            title='自己的报价', customer_name='客户A', created_by=staff_user)
        Quote.objects.create(
            title='他人的报价', customer_name='客户B', created_by=admin_user)
        allow('STAFF', 'QUOTE', 'view')

        response = client_for(staff_user).get('/api/dashboard/stats/')
        assert response.status_code == 200
        assert response.data['totals']['quote_count'] == 1
        assert response.data['totals']['product_count'] == 0
        assert [item['id'] for item in response.data['recent_activities']] == [own.id]