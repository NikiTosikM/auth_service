from core.db import db_core
from core.redis import redis_core


async def get_session_depen():
    async with db_core.get_async_session() as session:
        try:
            yield session
            await session.commit() 
        except Exception:
            await session.rollback()  
            raise
        finally:
            await session.close()


async def get_redis_client_depen():
    async with redis_core.create_client() as client:
        yield client
