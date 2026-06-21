import importlib

import pytest

from cognee.modules.ingestion.exceptions import IngestionError
from cognee.tasks.ingestion import ingestion_settings

storage_mod = importlib.import_module("cognee.tasks.ingestion.save_data_item_to_storage")


@pytest.mark.asyncio
async def test_http_ingestion_blocked_when_allow_http_requests_false(monkeypatch):
    monkeypatch.setenv("ALLOW_HTTP_REQUESTS", "false")
    storage_mod.settings = ingestion_settings.IngestionSettings()

    with pytest.raises(IngestionError, match="HTTP requests are not accepted"):
        await storage_mod.save_data_item_to_storage("http://127.0.0.1:9/probe")


@pytest.mark.asyncio
async def test_http_ingestion_allowed_when_allow_http_requests_true(monkeypatch):
    monkeypatch.setenv("ALLOW_HTTP_REQUESTS", "true")
    storage_mod.settings = ingestion_settings.IngestionSettings()

    from unittest.mock import AsyncMock, patch

    with patch(
        "cognee.tasks.ingestion.save_data_item_to_storage.fetch_page_content",
        new_callable=AsyncMock,
    ) as mock_fetch:
        mock_fetch.return_value = {"http://127.0.0.1:9/probe": "<html>ok</html>"}
        with patch(
            "cognee.tasks.ingestion.save_data_item_to_storage.save_data_to_file",
            new_callable=AsyncMock,
        ) as mock_save:
            mock_save.return_value = "file:///tmp/fake.html"
            result = await storage_mod.save_data_item_to_storage("http://127.0.0.1:9/probe")

    assert result == "file:///tmp/fake.html"
    mock_fetch.assert_awaited_once()
