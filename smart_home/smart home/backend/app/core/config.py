from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "smart-home-backend"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_prefix: str = "/api"

    database_host: str = "127.0.0.1"
    database_port: int = 3306
    database_name: str = "smart_home"
    database_user: str = "root"
    database_password: str = ""

    jwt_algorithm: str = "RS256"
    jwt_expire_minutes: int = 120
    jwt_private_key_path: str = "keys/private_key.pem"
    jwt_public_key_path: str = "keys/public_key.pem"
    jwt_mock_secret: str = "smart-home-dev-secret"

    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    use_mock_repository: bool = True
    simulation_enabled: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
