from datetime import datetime
import functools
import asyncio

from loguru import logger

logger.remove()

# обработчик для debug уровня
logger.add(
    f"logger_datas/debug_info_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log",
    format="<green>{time}</green> | {level} | <yellow>{file}</yellow> | {message}",
    level="DEBUG",
    rotation="10 MB",
)


# обработчик для error уровня
logger.add(
    f"logger_datas/errors_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log",
    format="<green>{time}</green> | <red>{level}</red> | <yellow>{name}</yellow> | {message}",
    level="ERROR",
    rotation="10 MB",
)


# декоратор для логирования endpoint
def log_endpoint(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Start endpoint - {func.__name__}. Parametrs - {args}, {kwargs}")
        start_time: datetime = datetime.now()

        try:
            result = func(*args, **kwargs)

            if asyncio.iscoroutine(result):
                result = await result

            end_time: datetime = datetime.now()
            logger.info(
                f"Endpoint - {func.__name__} completed execution. Time - {(end_time - start_time)}"
            )
            return result
        except Exception as ex:
            error_message = f"Endpoint - {func.__name__} failed with error: {str(ex)}"
            logger.error(error_message)
            raise

    return wrapper
