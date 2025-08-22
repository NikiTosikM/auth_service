from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


from core import settings


class DBCore():
    def __init__(self):
        self._async_engine = create_async_engine(
            url=settings.db.get_db_url,
            echo=True
        )
        self._async_session = async_sessionmaker(self._async_engine)
        
    @property
    def get_aync_session(self) -> async_sessionmaker[AsyncSession]:
        self._async_session
        
        
db_core = DBCore()