from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict



ROOT_DIR = Path(__file__).resolve().parent.parent.parent 


class ConfigApp(BaseModel):
    host: str = "localhost"
    port: int = "8000"
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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= ROOT_DIR / ".env",
        env_nested_delimiter="__",
    )
    
    app: ConfigApp = ConfigApp()
    db: DBConfig


settings = Settings()
