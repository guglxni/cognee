"""Regression tests for https://github.com/topoteretes/cognee/issues/3241"""

import importlib
from unittest.mock import AsyncMock, patch

import pytest

create_default_user_mod = importlib.import_module(
    "cognee.modules.users.methods.create_default_user"
)


@pytest.mark.asyncio
async def test_create_default_user_is_not_superuser_by_default(monkeypatch):
    monkeypatch.delenv("DEFAULT_USER_IS_SUPERUSER", raising=False)

    with patch.object(create_default_user_mod, "create_user", new_callable=AsyncMock) as mock_create_user:
        mock_create_user.return_value = object()
        await create_default_user_mod.create_default_user()

    assert mock_create_user.await_args.kwargs["is_superuser"] is False


@pytest.mark.asyncio
async def test_create_default_user_can_be_superuser_when_explicitly_enabled(monkeypatch):
    monkeypatch.setenv("DEFAULT_USER_IS_SUPERUSER", "true")

    with patch.object(create_default_user_mod, "create_user", new_callable=AsyncMock) as mock_create_user:
        mock_create_user.return_value = object()
        await create_default_user_mod.create_default_user()

    assert mock_create_user.await_args.kwargs["is_superuser"] is True
