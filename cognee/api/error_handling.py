import os

from cognee.exceptions.exceptions import CogneeApiError

GENERIC_INTERNAL_ERROR_DETAIL = "An unexpected error occurred. Please try again later."


def get_api_error_detail(error: Exception) -> str | None:
    """Return a client-safe error detail string for API responses."""
    if isinstance(error, CogneeApiError):
        return error.message

    if os.getenv("EXPOSE_INTERNAL_API_ERRORS", "false").lower() == "true":
        return str(error)

    return GENERIC_INTERNAL_ERROR_DETAIL
