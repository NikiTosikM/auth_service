from contextlib import asynccontextmanager

from redis.asyncio import ConnectionPool, Redis

from core import settings


class RedisCore:
    def __init__(self, host: str, port: int, db_num: int, max_connection: int):
        self._host = host
        self._port = port
        self._db_num = db_num
        self._max_connection = max_connection
        self._pool = None

    def create_connection_pool(self):
        if not self._pool:
            self._pool = ConnectionPool(
                host=self._host,
                port=self._port,
                db=self._db_num,
                max_connections=self._max_connection,
                decode_responses=True,
            )
        return self._pool

    @asynccontextmanager
    async def create_client(self):
        client = Redis(connection_pool=self._pool)
        try:
            yield client
        finally:
            await client.close()

    async def close_pool(self):
        if self._pool:
            await self._pool.disconnect()


redis_core = RedisCore(
    host=settings.redis.host,
    port=settings.redis.port,
    db_num=settings.redis.db_number,
    max_connection=settings.redis.max_connection_pool,
)
