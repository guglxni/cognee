import os

import pytest

from cognee.api.error_handling import (
    GENERIC_INTERNAL_ERROR_DETAIL,
    get_api_error_detail,
)
from cognee.exceptions.exceptions import CogneeValidationError


def test_unknown_exception_returns_generic_detail(monkeypatch):
    monkeypatch.delenv("EXPOSE_INTERNAL_API_ERRORS", raising=False)
    detail = get_api_error_detail(RuntimeError("INTERNAL_DB_HOST=10.0.0.99"))
    assert detail == GENERIC_INTERNAL_ERROR_DETAIL
    assert "10.0.0.99" not in detail


def test_cognee_api_error_message_is_preserved():
    detail = get_api_error_detail(CogneeValidationError(message="Dataset not found"))
    assert detail == "Dataset not found"


def test_internal_errors_can_be_exposed_when_explicitly_enabled(monkeypatch):
    monkeypatch.setenv("EXPOSE_INTERNAL_API_ERRORS", "true")
    detail = get_api_error_detail(RuntimeError("debug detail"))
    assert detail == "debug detail"
