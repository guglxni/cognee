"""Regression tests for https://github.com/topoteretes/cognee/issues/3235"""

import os
import pathlib
from uuid import uuid4

import pytest

import cognee
from cognee.api.v1.datasets import datasets
from cognee.modules.data.methods import create_authorized_dataset
from cognee.modules.engine.operations.setup import setup
from cognee.modules.data.exceptions.exceptions import UnauthorizedDataAccessError
from cognee.modules.users.methods import create_user
from cognee.modules.users.permissions.methods import authorized_give_permission_on_datasets


@pytest.mark.asyncio
async def test_delete_random_uuid_without_data_row_is_rejected():
    os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "True"

    root = pathlib.Path(__file__).parent / ".repro_delete_missing_row_unit"
    cognee.config.data_root_directory(str(root / "data"))
    cognee.config.system_root_directory(str(root / "system"))

    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)
    await setup()

    owner = await create_user(email="owner-delete-3235@example.com", password="password123")
    deleter = await create_user(email="deleter-delete-3235@example.com", password="password123")

    dataset = await create_authorized_dataset(dataset_name="shared_dataset_3235", user=owner)
    await authorized_give_permission_on_datasets(deleter.id, [dataset.id], "delete", owner.id)

    random_data_id = uuid4()

    with pytest.raises(UnauthorizedDataAccessError, match="not accessible"):
        await datasets.delete_data(dataset.id, random_data_id, user=deleter)
