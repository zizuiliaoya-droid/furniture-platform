"""Narrow, auditable endpoints exposed to agent clients."""
from time import perf_counter

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AgentActionAudit
from .services import (
    agent_request_id,
    public_web_url,
    record_agent_audit,
    visible_capabilities,
)


class AgentCapabilitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        started_at = perf_counter()
        request_id = agent_request_id(request)
        payload = {
            'schema_version': '1.0',
            'request_id': request_id,
            'web_url': public_web_url(),
            'capabilities': visible_capabilities(request.user),
        }
        record_agent_audit(
            request=request,
            request_id=request_id,
            action='system.capabilities',
            status=AgentActionAudit.Status.SUCCEEDED,
            started_at=started_at,
            input_data={'method': request.method, 'path': request.path},
            output_data={'capability_count': len(payload['capabilities'])},
        )
        response = Response(payload)
        response['X-Request-ID'] = request_id
        return response
