"""Evidence for #3239 — ALLOW_CYPHER_QUERY defaults to true."""

import os

from cognee.modules.search.methods.get_search_type_retriever_instance import (
    get_search_type_retriever_instance,
)
from cognee.modules.search.types import SearchType


async def main() -> None:
    os.environ.pop("ALLOW_CYPHER_QUERY", None)
    default = os.getenv("ALLOW_CYPHER_QUERY", "true")
    print("ALLOW_CYPHER_QUERY unset => effective default:", default)

    # Should not raise when default is true
    retriever = await get_search_type_retriever_instance(
        SearchType.CYPHER,
        query_text="MATCH (n) RETURN n LIMIT 1",
    )
    print("CYPHER retriever class:", type(retriever).__name__)

    os.environ["ALLOW_CYPHER_QUERY"] = "false"
    try:
        await get_search_type_retriever_instance(
            SearchType.CYPHER,
            query_text="MATCH (n) RETURN n LIMIT 1",
        )
        print("With ALLOW_CYPHER_QUERY=false: retriever still created (unexpected)")
    except Exception as exc:
        print("With ALLOW_CYPHER_QUERY=false: blocked as expected:", type(exc).__name__)

    print("BUG: Cypher enabled by default; user query_text passed to graph_engine.query()")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
