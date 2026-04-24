"""Global exception handler for DRF."""
import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        logger.error('Unhandled exception: %s', exc, exc_info=True)
        return Response({'detail': 'Internal server error'}, status=500)
    return response
