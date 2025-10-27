from contextlib import asynccontextmanager
import sys
from pathlib import Path

from fastapi import FastAPI
import uvicorn

sys.path.append(str(Path(__file__).parent))

from src.core import settings
from src.auth.api import main_router
from src.auth.exception import (
    user_error_handlers,
    token_error_handler,
    server_error_handler,
)
from src.core.redis import redis_core


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_core.create_connection_pool()

    yield

    await redis_core.close_pool()


app = FastAPI()
app.include_router(main_router)

user_error_handlers(app)
token_error_handler(app)
server_error_handler(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload,
    )
