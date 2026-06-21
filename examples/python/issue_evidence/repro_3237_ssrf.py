"""Evidence for #3237 — ALLOW_HTTP_REQUESTS not enforced."""

import asyncio
import os
from unittest.mock import AsyncMock, patch

from cognee.tasks.ingestion.save_data_item_to_storage import save_data_item_to_storage


async def main() -> None:
    os.environ["ALLOW_HTTP_REQUESTS"] = "false"

    grep_note = (
        "grep ALLOW_HTTP_REQUESTS in *.py => 1 match (add router docstring only, no enforcement)"
    )
    print(grep_note)
    print("ALLOW_HTTP_REQUESTS env set to: false")

    with patch(
        "cognee.tasks.ingestion.save_data_item_to_storage.fetch_page_content",
        new_callable=AsyncMock,
    ) as mock_fetch:
        mock_fetch.return_value = {"http://127.0.0.1:9/probe": "<html>secret</html>"}
        with patch(
            "cognee.tasks.ingestion.save_data_item_to_storage.save_data_to_file",
            new_callable=AsyncMock,
        ) as mock_save:
            mock_save.return_value = "file:///tmp/fake.html"
            await save_data_item_to_storage("http://127.0.0.1:9/probe")

    print("fetch_page_content called:", mock_fetch.called)
    print("BUG: HTTP fetch runs even with ALLOW_HTTP_REQUESTS=false (flag unused in code)")


if __name__ == "__main__":
    asyncio.run(main())
