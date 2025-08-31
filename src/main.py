from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from core import settings
from auth.api import main_router
from auth.exception import user_error_handlers
from core.redis import redis_core



@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_core.create_connection_pool()
    
    yield
    
    await redis_core.close_pool()


app = FastAPI()
app.include_router(main_router)

user_error_handlers(app)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload
    )
