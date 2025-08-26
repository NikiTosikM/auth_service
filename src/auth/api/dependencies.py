from core.db import db_core


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

