from fastapi import FastAPI, Request, status, HTTPException

from src.auth.exception.exception import (
    TokenException,
    TokenNotValidException,
    TokenExpiredException,
    TokenSignatureException,
)


def token_error_handler(app: FastAPI):
    """Обработчик, работающий с ошибками токена"""

    @app.exception_handler(TokenNotValidException)
    @app.exception_handler(TokenSignatureException)
    @app.exception_handler(TokenExpiredException)
    def token_exception(request: Request, exc: TokenException):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": exc.detail},
        )

