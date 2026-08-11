"""Small unauthenticated operational endpoints."""

from django.db import connection
from django.http import JsonResponse
from django.views.static import serve
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


@require_GET
def media_view(request, path, document_root=None):
    """Serve legacy local media with a sandbox if a file is opened directly."""
    response = serve(request, path, document_root=document_root)
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cross-Origin-Resource-Policy'] = 'same-origin'
    response['Content-Security-Policy'] = "default-src 'none'; sandbox"
    return response
