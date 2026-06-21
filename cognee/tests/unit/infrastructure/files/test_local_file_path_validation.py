import importlib
from pathlib import Path

import pytest

from cognee.modules.ingestion.exceptions import IngestionError
from cognee.infrastructure.files.utils.local_file_path_validation import validate_local_file_path

storage_mod = importlib.import_module("cognee.tasks.ingestion.save_data_item_to_storage")


@pytest.mark.asyncio
async def test_relative_file_under_cwd_is_accepted(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    secret = tmp_path / "notes.txt"
    secret.write_text("hello", encoding="utf-8")

    uri = await storage_mod.save_data_item_to_storage("notes.txt")

    assert uri == secret.resolve().as_uri()


@pytest.mark.asyncio
async def test_absolute_path_outside_allowed_roots_is_rejected():
    with pytest.raises(IngestionError, match="outside allowed directories"):
        await storage_mod.save_data_item_to_storage("/etc/hosts")


def test_allowed_prefix_permits_configured_path(tmp_path, monkeypatch):
    outside = tmp_path / "outside"
    outside.mkdir()
    target = outside / "secret.txt"
    target.write_text("ok", encoding="utf-8")

    monkeypatch.setenv("ALLOWED_LOCAL_FILE_PATH_PREFIXES", str(outside))
    validated = validate_local_file_path(target)
    assert validated == target.resolve()


def test_validate_rejects_path_outside_roots(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(IngestionError, match="outside allowed directories"):
        validate_local_file_path(Path("/etc/passwd"))
