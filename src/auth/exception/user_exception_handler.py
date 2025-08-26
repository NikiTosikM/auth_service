from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from auth.exception.exception import UserAlreadeRegistered


def user_error_handlers(app: FastAPI):
    """Обработчик, связанный с пользовательскими ошибками"""

    @app.exception_handler(UserAlreadeRegistered)
    def user_already_registered(request: Request, exc: UserAlreadeRegistered):
        """Обработка ошибки когда пользователь уже зарегистрирован"""
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Re-registration of the user",
                "detail": "A user with this email address is already registered. Select a different email",
                "content": {
                    "email": exc.email
                }
            },
        )
