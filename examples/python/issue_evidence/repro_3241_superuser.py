"""Evidence for #3241 — unauthenticated caller becomes default superuser."""

import asyncio
import importlib
import os
import sys


async def main() -> None:
    os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
    os.environ.pop("REQUIRE_AUTHENTICATION", None)

    mod_name = "cognee.modules.users.methods.get_authenticated_user"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    gau = importlib.import_module(mod_name)

    print("REQUIRE_AUTHENTICATION:", gau.REQUIRE_AUTHENTICATION)
    print("ENABLE_BACKEND_ACCESS_CONTROL:", gau.ENABLE_BACKEND_ACCESS_CONTROL)

    user = await gau.get_authenticated_user(user=None)
    print("Unauthenticated caller resolved to email:", user.email)
    print("is_superuser:", user.is_superuser)
    assert user.is_superuser is True
    print("BUG: no token => default superuser when ENABLE_BACKEND_ACCESS_CONTROL=false")


if __name__ == "__main__":
    asyncio.run(main())
