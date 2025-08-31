from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict



ROOT_DIR = Path(__file__).resolve().parent.parent.parent 
BASE_DIR = Path(__file__).resolve().resolve().parent


class ConfigApp(BaseModel):
    host: str = "localhost"
    port: int = 8000
    reload: bool = True


class DBConfig(BaseModel):
    host: str = "localhost"
    port: int = "5432"
    username: str = "postgres"
    password: str
    name: str

    @property
    def get_db_url(self):
        url = ("postgresql+asyncpg://"
               f"{self.username}:{self.password}"
               f"@{self.host}:{self.port}"
               f"/{self.name}"
            )
        return url
    
class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    max_connection_pool: int = 10
    db_number: int = 0
    

class AuthSetting(BaseModel):
    private_key: Path = BASE_DIR / "keys" /  "private.xml"
    public_key: Path = BASE_DIR / "keys" / "public.xml"
    algorithm: str = "RS256"
    access_token_lifetime_minutes: int = 15
    refresh_token_lifetime_minutes: int = 10800


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= ROOT_DIR / ".env",
        env_nested_delimiter="__",
    )
    
    app: ConfigApp
    db: DBConfig
    auth: AuthSetting = AuthSetting()
    redis: RedisConfig

settings = Settings()
