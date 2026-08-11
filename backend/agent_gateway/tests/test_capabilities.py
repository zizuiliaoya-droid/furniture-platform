"""Agent Gateway 能力发现契约测试。"""
from uuid import UUID

import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestAgentCapabilities:
    def test_authentication_is_required(self):
        response = APIClient().get('/api/agent/capabilities/')

        assert response.status_code == 401

    def test_authenticated_agent_gets_machine_readable_contract(self, admin_user):
        token = Token.objects.create(user=admin_user)
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}',
            HTTP_X_AGENT_SKILL='furniture-system',
        )

        response = client.get('/api/agent/capabilities/')

        assert response.status_code == 200
        assert response.data['schema_version'] == '1.0'
        UUID(response.data['request_id'])
        assert response.data['web_url']
        capability = response.data['capabilities'][0]
        assert set(capability) >= {
            'name', 'description', 'method', 'path', 'mode',
            'required_permission', 'requires_confirmation',
        }

    def test_capability_request_is_audited(self, admin_user):
        from agent_gateway.models import AgentActionAudit

        token = Token.objects.create(user=admin_user)
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}',
            HTTP_X_AGENT_SKILL='furniture-system',
            HTTP_X_REQUEST_ID='d5ef1d43-d9aa-465a-afaf-ea30ae93aa70',
        )

        response = client.get('/api/agent/capabilities/')

        assert response.status_code == 200
        audit = AgentActionAudit.objects.get()
        assert audit.user == admin_user
        assert audit.skill_name == 'furniture-system'
        assert audit.action == 'system.capabilities'
        assert audit.status == AgentActionAudit.Status.SUCCEEDED
        assert audit.request_id == 'd5ef1d43-d9aa-465a-afaf-ea30ae93aa70'
        assert audit.duration_ms >= 0
