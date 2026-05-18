from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = (
        "postgresql://qts:qts_dev_change_me@127.0.0.1:5432/quatangshi"
    )
    meili_host: str = "http://127.0.0.1:7700"
    meili_api_key: str = "dev-master-key-change-me"
    meili_index: str = "quatangshi"
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"


settings = Settings()
