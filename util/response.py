from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from functools import wraps
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
    ObjectDoesNotExist,
)
from django.http import Http404
from django.db import IntegrityError, DatabaseError, transaction
from rest_framework.exceptions import (
    APIException,
    ValidationError as DRFValidationError,
    NotFound,
    PermissionDenied,
)
import logging

logger = logging.getLogger(__name__)

from math import ceil


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        total_items = self.page.paginator.count
        current_page = self.page.number
        per_page = self.page.paginator.per_page
        total_pages = ceil(total_items / int(per_page))

        return custom_response(
            status_text="success",
            message="Success",
            data={
                "count": total_items,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "current_page": current_page,
                "total_pages": total_pages,
                "page_size": int(per_page),
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "results": data,
            },
            status_code=status.HTTP_200_OK,
        )


def custom_response(status_text, data=None, message=None, errors=None, status_code=200):
    return Response(
        {
            "status": status_text,
            "message": message or "Success",
            "data": data,
            "errors": errors,
        },
        status=status_code,
    )


def handle_custom_exceptions():
    """
    Universal decorator to catch and handle all common exceptions
    for both function-based and class-based views.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            try:
                return view_func(*args, **kwargs)

            # Common Django ORM exception
            except ObjectDoesNotExist:
                return Response(
                    {"status": "error", "message": "Requested object not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # DRF NotFound exception
            except NotFound as e:
                return Response(
                    {"status": "error", "message": str(e) or "Resource not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Integrity / constraint violations
            except IntegrityError as e:
                logger.exception("Database integrity error")
                return Response(
                    {
                        "status": "error",
                        "message": "Database integrity constraint violated.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validation exceptions (both DRF & Django)
            except (DRFValidationError, DjangoValidationError) as e:
                return Response(
                    {
                        "status": "error",
                        "message": e.message if hasattr(e, "message") else str(e),
                        "errors": getattr(e, "detail", None),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Permission issues
            except PermissionDenied as e:
                return Response(
                    {
                        "status": "error",
                        "message": str(e)
                        or "You do not have permission to perform this action.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Any other uncaught exceptions
            except Exception as e:
                logger.exception("Unexpected server error")
                return Response(
                    {"status": "error", "message": "An unexpected error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return _wrapped_view

    return decorator


from rest_framework.views import exception_handler as drf_exception_handler


class ExceptionHandlerMixin:
    """
    Mixin to attach to any DRF CBV (APIView, GenericAPIView, ViewSet, ModelViewSet, etc.)
    - Overrides handle_exception to return `custom_response`
    - Provides helpers success_response / error_response for consistency
    """

    default_error_message = "An unexpected error occurred."

    # ---- helper wrappers for consistent success/error responses ----
    def success_response(
        self, message="Success", data=None, status_code=status.HTTP_200_OK
    ):
        return custom_response(
            status_text="success",
            message=message,
            data=data if data is not None else {},
            status_code=status_code,
        )

    def error_response(
        self, message="Error", errors=None, status_code=status.HTTP_400_BAD_REQUEST
    ):
        # pass `errors` if your custom_response supports it (your earlier snippets did)
        kwargs = {
            "status_text": "error",
            "message": message,
            "status_code": status_code,
        }
        if errors is not None:
            kwargs["errors"] = errors
        return custom_response(**kwargs)

    # ---- main exception funnel ----
    def handle_exception(self, exc):
        # Django "not found"
        if isinstance(exc, (ObjectDoesNotExist,)):
            return self.error_response(
                message="The requested resource was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # DRF / Django validation errors
        if isinstance(exc, (DRFValidationError, DjangoValidationError)):
            errors = getattr(exc, "detail", None) or (
                exc.message_dict if hasattr(exc, "message_dict") else str(exc)
            )
            return self.error_response(
                message="Validation failed.",
                errors=errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # DB integrity errors
        if isinstance(exc, IntegrityError):
            logger.exception("Database integrity error")
            return self.error_response(
                message="A database integrity error occurred (constraint violation).",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Generic DB errors
        if isinstance(exc, DatabaseError):
            logger.exception("Database error")
            return self.error_response(
                message="A database error occurred while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # DRF APIExceptions (PermissionDenied, NotAuthenticated, NotFound etc.)
        if isinstance(exc, APIException):
            detail = getattr(exc, "detail", str(exc))
            code = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)
            return self.error_response(message=str(detail), status_code=code)

        # fallback to DRF's handler (to get standard behavior for other cases)
        drf_response = drf_exception_handler(exc, None)
        if drf_response is not None:
            # convert DRF response body into our custom_response wrapper
            body = drf_response.data if hasattr(drf_response, "data") else {}
            return self.error_response(
                message="Request failed.",
                errors=body,
                status_code=drf_response.status_code,
            )

        # final catch-all
        logger.exception("Unhandled exception")
        return self.error_response(
            message=self.default_error_message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
