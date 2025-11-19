from httpx import Response
from sqlalchemy import select, Result

from src.auth.models.user import User


async def test_register(create_client, get_test_async_session):
    register_responce: Response = await create_client.post(
        url="/auth/register",
        json={
            "name": "usernametest",
            "last_name": "lastnameuser",
            "email": "usermailtest@mail.ru",
            "password": "12345passworduser!",
            "role": "user",
        },
    )

    assert register_responce.status_code == 200
    assert register_responce.json()

    get_user_query = select(User).filter_by(email="usermailtest@mail.ru")
    result: Result = await get_test_async_session.execute(get_user_query)
    model = result.scalar_one()

    assert model


async def test_login(create_client):
    authentication_responce: Response = await create_client.post(
        url="/auth/login",
        json={"login": "usermailtest@mail.ru", "password": "12345passworduser!"},
    )
    auth_data = authentication_responce.json()

    assert authentication_responce.status_code == 200
    assert all(token in ["access_token", "refresh_token"] for token in auth_data)


async def test_protected(authentication_user):
    access_token = authentication_user.headers.get("access_token")

    protected_responce: Response = await authentication_user.get(
        url="/auth/protected",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert protected_responce.status_code == 200
    assert protected_responce.json().get("status")


async def test_logout(authentication_user):
    access_token = authentication_user.headers.get("access_token")

    auth_responce: Response = await authentication_user.post(
        url="/auth/logout",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert auth_responce.status_code == 200

