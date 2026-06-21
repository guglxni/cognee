"""Evidence for #3238 — local file read via ingestion."""

import asyncio
import os
import pathlib
import tempfile

from cognee.infrastructure.files.utils.open_data_file import open_data_file
from cognee.tasks.ingestion.save_data_item_to_storage import save_data_item_to_storage


async def main() -> None:
    os.environ.pop("ACCEPT_LOCAL_FILE_PATH", None)

    with tempfile.TemporaryDirectory() as tmp:
        secret = pathlib.Path(tmp) / "secret.txt"
        marker = "COGNEE_LOCAL_FILE_PROBE_998877"
        secret.write_text(marker, encoding="utf-8")

        uri = await save_data_item_to_storage(str(secret))
        async with open_data_file(uri) as handle:
            content = handle.read().decode("utf-8", errors="replace")

        print("input path:", secret)
        print("stored uri:", uri)
        print("marker in stored content:", marker in content)
        assert marker in content
        print("accept_local_file_path default: True (no env override)")
        print("BUG: host file read into Cognee storage without allowlist/traversal checks")


if __name__ == "__main__":
    asyncio.run(main())
