from contextlib import asynccontextmanager

from redis.asyncio import ConnectionPool, Redis, ConnectionError, TimeoutError, RedisError
from loguru import logger

from src.core.config import settings
from src.auth.exception.exception import RedisConnectionException, RedisTimeoutException,  RedisException



class RedisCore:
    def __init__(self, host: str, port: int, db_num: int, max_connection: int):
        self._host = host
        self._port = port
        self._db_num = db_num
        self._max_connection = max_connection
        self._pool = None

    def create_connection_pool(self):
        try:
            if not self._pool:
                self._pool = ConnectionPool(
                    host=self._host,
                    port=self._port,
                    db=self._db_num,
                    max_connections=self._max_connection,
                    decode_responses=True,
                )
            return self._pool
        except ConnectionError as error:
            logger.error(f"Ошибка подключения к Redis - {error}")
            raise RedisConnectionException from error
        except TimeoutError as error:
            logger.error(f"Вышло время подключения к Redis - {error}")
            raise RedisTimeoutException from error
        except RedisError as error:
            logger.error(f"Ошибка Redis - {error}")
            raise RedisException from error
    
    async def test_request(self):
        """ Проверяет подключение к Redis при запуске приложения """
        try:
            client = Redis(connection_pool=self._pool)
            await client.ping()
            logger.info("Тестовое подключение к Redis успешно ")
        except RedisError as error:
            logger.error(f"Ошибка Redis - {error}")
            raise RedisException from error
            
        

    @asynccontextmanager
    async def create_client(self):
        client = Redis(connection_pool=self._pool)
        try:
            yield client
        finally:
            await client.aclose()

    async def close_pool(self):
        if self._pool:
            await self._pool.disconnect()


redis_core = RedisCore(
    host=settings.redis.host,
    port=settings.redis.port,
    db_num=settings.redis.db_number,
    max_connection=settings.redis.max_connection_pool,
)
