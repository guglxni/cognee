"""Minimal repro for https://github.com/topoteretes/cognee/issues/3235

Shows delete_data() returns success for a random data_id with no relational
Data row in the dataset, skipping the membership check on the normal path.
"""

import asyncio
import os
import pathlib
from uuid import uuid4

import cognee
from cognee.api.v1.datasets import datasets
from cognee.modules.data.methods import create_authorized_dataset
from cognee.modules.engine.operations.setup import setup
from cognee.modules.users.methods import create_user
from cognee.modules.users.permissions.methods import authorized_give_permission_on_datasets


async def main() -> None:
    os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "True"

    root = pathlib.Path(__file__).parent / ".repro_delete_missing_row"
    cognee.config.data_root_directory(str(root / "data"))
    cognee.config.system_root_directory(str(root / "system"))

    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)
    await setup()

    owner = await create_user(email="owner@example.com", password="password123")
    deleter = await create_user(email="deleter@example.com", password="password123")

    dataset = await create_authorized_dataset(dataset_name="shared_dataset", user=owner)
    await authorized_give_permission_on_datasets(deleter.id, [dataset.id], "delete", owner.id)

    random_data_id = uuid4()
    result = await datasets.delete_data(dataset.id, random_data_id, user=deleter)

    print("dataset_id:", dataset.id)
    print("random_data_id:", random_data_id)
    print("delete_data result:", result)

    assert result == {"status": "success"}, (
        "Expected success without relational Data row — membership check was skipped"
    )
    print("Repro confirmed: delete succeeded for unrelated UUID with no Data row.")


if __name__ == "__main__":
    asyncio.run(main())
