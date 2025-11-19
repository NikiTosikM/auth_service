from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient, Response
from redis.asyncio import Redis
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.auth.api.dependencies import get_redis_client_depen, get_session_depen
from src.auth.service import RedisManager
from src.core.config import settings
from src.core.db.base_model import Base
from src.main import app

app.router.lifespan_context = None

async_engine = create_async_engine(settings.db.get_db_url, poolclass=NullPool)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


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
    async with Redis(host=settings.redis.host, port=settings.redis.port) as redis_client:
        yield RedisManager(client=redis_client)


app.dependency_overrides[get_session_depen] = get_async_session
app.dependency_overrides[get_redis_client_depen] = get_async_redis_client


@pytest.fixture()
async def get_test_async_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session


@pytest.fixture()
async def get_redis_client_fixture() -> AsyncGenerator[RedisManager, None]:
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

    create_client.headers["access_token"] = auth_data.get("access_token")
    create_client.cookies.set("refresh_token", auth_data.get("refresh_token"))

    yield create_client
