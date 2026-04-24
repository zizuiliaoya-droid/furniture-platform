"""Dashboard views."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import DashboardService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_view(request):
    stats = DashboardService.get_stats()
    return Response(stats)
