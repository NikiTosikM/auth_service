from fastapi import FastAPI
import uvicorn

from core import settings


app = FastAPI()



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload
    )
