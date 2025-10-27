from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
import pytest
from httpx import AsyncClient, ASGITransport, Response
from typing import AsyncGenerator

from redis import Redis

from src.auth.api.dependencies import get_session_depen, get_redis_client_depen
from src.core.config import settings
from src.core.db.base_model import Base
from src.core.redis import redis_core
from src.auth.service import RedisManager
from src.main import app


async_engine = create_async_engine(settings.db.get_db_url, poolclass=NullPool)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)

client_redis: Redis = Redis(host=settings.redis.host, port=settings.redis.port)


@pytest.fixture(scope="session", autouse=True)
async def setting_up_db():
    assert settings.mode == "Test"

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session():
    async with async_session_maker() as async_session:
        yield async_session
        await async_session.commit()


async def get_async_redis_client() -> AsyncGenerator[RedisManager, None]:
    async with redis_core.create_client() as client:
        yield RedisManager(client=client)


app.dependency_overrides[get_session_depen] = get_async_session
app.dependency_overrides[get_redis_client_depen] = get_async_redis_client


@pytest.fixture()
async def get_test_async_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session


@pytest.fixture()
async def get_redis_client_depen() -> AsyncGenerator[RedisManager, None]:
    async for session in get_async_redis_client():
        yield session


@pytest.fixture(scope="session")
async def create_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client


@pytest.fixture(scope="session")
async def register_user(create_client):
    register_responce: Response = await create_client.post(
        url="/auth/register",
        json={
            "name": "username",
            "last_name": "lastnameuser",
            "email": "usermail@mail.ru",
            "password": "12345passworduser!",
            "role": "user",
        },
    )

    assert register_responce.status_code == 200
    assert register_responce.json()


@pytest.fixture(scope="session")
async def authentication_user(create_client: AsyncClient, register_user):
    authentication_responce: Response = await create_client.post(
        url="/auth/login",
        json={"login": "usermail@mail.ru", "password": "12345passworduser!"},
    )
    auth_data = authentication_responce.json()

    assert authentication_responce.status_code == 200
    assert all(token in ["access_token", "refresh_token"] for token in auth_data)

    create_client.cookies.update(auth_data)

    yield create_client
