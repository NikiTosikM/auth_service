from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from auth.exception.exception import UserAlreadeRegistered, IncorrectUserLoginData


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
                "content": {"email": exc.email},
            },
        )

    @app.exception_handler(IncorrectUserLoginData)
    def incorrect_user_login_data(request: Request, exc: IncorrectUserLoginData):
        """Обработка ошибки когда пользователь ввел неверные данные при входе"""
        return ORJSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "message": exc.message,
                "detail": "Сheck the accuracy of the entered data",
                "content": {"email": exc.login, "password": exc.password},
            },
        )
