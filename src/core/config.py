from pathlib import Path
from typing import Literal

from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = Path(__file__).resolve().parent.parent


class ConfigApp(BaseModel):
    host: str = "localhost"
    port: int = 8000
    reload: bool = True


class DBConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str
    name: str

    @property
    def get_db_url(self):
        url = (
            "postgresql+asyncpg://"
            f"{self.username}:{self.password}"
            f"@{self.host}:{self.port}"
            f"/{self.name}"
        )
        return url


class RedisConfig(BaseModel):
    host: str
    port: int
    max_connection_pool: int = 10
    db_number: int = 0

    @property
    def get_redis_url(self):
        return f"redis://{self.host}:{self.port}"


class EmailConfig(BaseModel):
    sender_email: EmailStr
    sender_password: str


class AuthSetting(BaseModel):
    private_key: Path = BASE_DIR / "keys" / "private.pem"
    public_key: Path = BASE_DIR / "keys" / "public.pem"
    algorithm: str = "RS256"
    access_token_lifetime_minutes: int = 15
    refresh_token_lifetime_minutes: int = 10800


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_nested_delimiter="__",
    )
    mode: Literal["Prod", "Test", "Local", "Dev"]
    app: ConfigApp
    db: DBConfig
    auth: AuthSetting = AuthSetting()
    redis: RedisConfig
    email: EmailConfig


settings = Settings()
