"""Regression test for https://github.com/topoteretes/cognee/issues/3240"""

from types import SimpleNamespace
from uuid import uuid4

import pytest

import cognee.api.v1.add as add_pkg
from cognee.api.error_handling import GENERIC_INTERNAL_ERROR_DETAIL
from cognee.api.v1.add.routers.get_add_router import get_add_router


@pytest.mark.asyncio
async def test_add_router_does_not_leak_internal_exception_strings():
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
        assert "10.0.0.99" not in body
        assert GENERIC_INTERNAL_ERROR_DETAIL in body
    finally:
        add_pkg.add = original
