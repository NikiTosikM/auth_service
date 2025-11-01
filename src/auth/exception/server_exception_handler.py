from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from src.auth.exception.exception import RedisConnectionException, RedisTimeoutException, RedisException


def server_error_handler(app: FastAPI):
    """Обработка всех серверных ошибок"""

    @app.exception_handler(RedisConnectionException)
    @app.exception_handler(RedisTimeoutException)
    async def redis_errors(request: Request, exc: RedisException):
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Internal server error",
                "error": "Unexpected error has occurred",
            },
        )
