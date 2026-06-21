"""Evidence for #3240 — raw exception strings in API responses."""

import asyncio
from types import SimpleNamespace
from uuid import uuid4


async def main() -> None:
    import cognee.api.v1.add as add_pkg
    from cognee.api.v1.add.routers.get_add_router import get_add_router

    router = get_add_router()
    add_route = next(r for r in router.routes if getattr(r, "path", "") == "")

    user = SimpleNamespace(id=uuid4(), tenant_id=None)

    async def boom(*_args, **_kwargs):
        raise RuntimeError("INTERNAL_DB_HOST=10.0.0.99 connection refused")

    original = add_pkg.add
    add_pkg.add = boom
    try:
        response = await add_route.endpoint(
            data=[],
            datasetName="probe",
            datasetId=None,
            node_set=None,
            run_in_background=False,
            user=user,
        )
        body = response.body.decode()
        print("HTTP status:", response.status_code)
        print("Response body:", body)
        assert "10.0.0.99" in body
        print("BUG: internal exception string leaked in JSON detail field")
    finally:
        add_pkg.add = original


if __name__ == "__main__":
    asyncio.run(main())
