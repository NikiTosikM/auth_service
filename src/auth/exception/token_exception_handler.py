from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from auth.exception.exception import TokenValidException


def token_error_handler(app: FastAPI):
    """ Обработчик, работающий с ошибками токена """
    @app.exception_handler(TokenValidException)
    def token_not_valid(request: Request, exc: TokenValidException):
        return ORJSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": "Token is not valid"
            }
        )
        