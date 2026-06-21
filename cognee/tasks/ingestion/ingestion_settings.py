from pydantic_settings import BaseSettings, SettingsConfigDict


class IngestionSettings(BaseSettings):
    accept_local_file_path: bool = True
    allow_http_requests: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = IngestionSettings()
