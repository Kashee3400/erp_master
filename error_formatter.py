# utils/error_formatter.py

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.exceptions import ErrorDetail


def format_exception(exc, context_data=None, context_label="context"):
    """
    Generic structured error formatter for API or background logic.

    Args:
        exc (Exception): The exception instance.
        context_data (dict, optional): Any contextual data related to the error.
        context_label (str, optional): Label for the context data (e.g., "member_data", "input", etc.).

    Returns:
        dict: A structured and user-friendly error response.
    """
    error_response = {}

    if context_data is not None:
        error_response[context_label] = context_data

    if isinstance(exc, ObjectDoesNotExist):
        error_response.update(
            {
                "error_type": "ReferenceError",
                "message": "Linked record not found. Please ensure referenced object exists.",
            }
        )

    elif isinstance(exc, ValidationError):
        error_dict = exc.message_dict if hasattr(exc, "message_dict") else exc.detail
        friendly_errors = {}

        for field, errs in error_dict.items():
            messages = [str(err) for err in errs]
            friendly_errors[field] = messages

        error_response.update(
            {
                "error_type": "ValidationError",
                "message": "Some fields contain invalid or missing data.",
                "details": friendly_errors,
            }
        )

    else:
        error_response.update(
            {
                "error_type": "UnexpectedError",
                "message": "An unexpected error occurred.",
                "details": str(exc),
            }
        )

    return error_response

def simplify_errors(error_detail):
    """
    Converts DRF ErrorDetail or nested error lists/dicts into plain string messages.
    """
    if isinstance(error_detail, dict):
        return {k: simplify_errors(v) for k, v in error_detail.items()}
    elif isinstance(error_detail, list):
        return [str(e) for e in error_detail]
    else:
        return str(error_detail)
