from fastapi import FastAPI, Request, status, HTTPException

from src.auth.exception.exception import (
    RedisConnectionException,
    RedisTimeoutException,
    RedisException,
    OperationDBException,
    LongRequestTimeExecution,
    DBException,
)


def server_error_handler(app: FastAPI):
    """Обработка всех серверных ошибок"""
    server_http_exception = HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Internal server error",
                "error": "Unexpected error has occurred",
            },
        )

    @app.exception_handler(RedisConnectionException)
    @app.exception_handler(RedisTimeoutException)
    def redis_errors(request: Request, exc: RedisException):
        raise server_http_exception
        
    @app.exception_handler(OperationDBException)
    @app.exception_handler(LongRequestTimeExecution)
    def db_errors(request: Request, exc: DBException):
        raise server_http_exception

    @app.exception_handler(Exception)
    def server_exception(request: Request, exc: Exception):
        raise server_http_exception