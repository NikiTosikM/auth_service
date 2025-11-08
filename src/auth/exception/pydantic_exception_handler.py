from fastapi import FastAPI, Request, HTTPException, status

from src.auth.exception.exception import (
    UserEmailShortException,
    UserLastNameShortException,
    UserNameShortException,
    UserPasswordUncorrctedException,
)


def pydantic_error_handler(app: FastAPI):
    def return_json_repsonce(message: str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message
        )
    
    @app.exception_handler(UserNameShortException)
    def user_name_short(request: Request, exc: UserNameShortException):
        '''  Обработчик ошибки короткого пароля   '''
        return_json_repsonce(message=exc.detail)
        
    @app.exception_handler(UserLastNameShortException)
    def user_lastname_short(request: Request, exc: UserLastNameShortException):
        ''' Обработчик ошибки короткой фамилии '''
        return_json_repsonce(message=exc.detail)
    
    @app.exception_handler(UserEmailShortException)
    def user_email_short(request: Request, exc: UserEmailShortException):
        ''' Обработчик короткого email '''
        return_json_repsonce(message=exc.detail)
        
    @app.exception_handler(UserPasswordUncorrctedException)
    def user_password_short(request: Request, exc: UserPasswordUncorrctedException):
        '''  Обработчик короткого пароля '''
        return_json_repsonce(message=exc.detail)
        
        
        
    