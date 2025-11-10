from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from shared.domain.exceptions import DomainError, NotFoundError, PermissionError, ValidationError


def pixelcheck_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, ValidationError):
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    if isinstance(exc, NotFoundError):
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
    if isinstance(exc, PermissionError):
        return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
    if isinstance(exc, DomainError):
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return response
