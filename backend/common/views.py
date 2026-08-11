"""Small unauthenticated operational endpoints."""

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health_view(request):
    """Report readiness without exposing application or database details."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except Exception:
        return JsonResponse(
            {'status': 'unavailable', 'service': 'furniture-api'},
            status=503,
        )

    return JsonResponse({'status': 'ok', 'service': 'furniture-api'})
