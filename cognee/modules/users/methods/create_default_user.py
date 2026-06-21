import os

from .create_user import create_user
from cognee.base_config import get_base_config


async def create_default_user():
    base_config = get_base_config()
    default_user_email = base_config.default_user_email or "default_user@example.com"
    default_user_password = base_config.default_user_password or "default_password"
    is_superuser = os.getenv("DEFAULT_USER_IS_SUPERUSER", "false").lower() == "true"

    user = await create_user(
        email=default_user_email,
        password=default_user_password,
        is_superuser=is_superuser,
        is_active=True,
        is_verified=True,
        auto_login=True,
    )

    return user
