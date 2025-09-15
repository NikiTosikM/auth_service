from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse


def server_error_handler(app: FastAPI):
    ''' Обработка все серверных ошибок '''
    @app.exception_handler(Exception)
    def redis_errors(request: Request, exc: Exception):
        # добавить запись в logger
        
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Internal server error",
                "error": "Unexpected error has occurred"
            }
        )
        