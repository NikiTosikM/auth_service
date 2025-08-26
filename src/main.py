from fastapi import FastAPI
import uvicorn

from core import settings
from auth.api import main_router
from auth.exception import user_error_handlers


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
