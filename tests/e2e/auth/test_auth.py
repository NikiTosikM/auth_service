from httpx import Response, AsyncClient
import pytest

from tests.parametrize_data.auth_data import datas_for_test_full_check_user


@pytest.mark.parametrize(
    "name, last_name, email ,password ,role ,status_code",
    datas_for_test_full_check_user,
)
async def test_full_check_user(
    name,
    last_name,
    email,
    password,
    role,
    status_code,
    create_client: AsyncClient,
    get_redis_client_fixture,
):
    # создаем
    register_responce: Response = await create_client.post(
        url="/auth/register",
        json={
            "name": name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "role": role,
        },
    )
    responce_data = register_responce.json()
    register_status = register_responce.status_code == status_code

    assert register_status

    if register_status != 200:
        return

    assert all(parametr in ["id", "email", "role"] for parametr in responce_data)

    # аутентификация
    login_responce: Response = await create_client.post(
        url="/auth/login", json={"login": email, "password": password}
    )
    login_data = login_responce.json()

    assert login_responce.status_code == status_code
    assert all(token in ["access_token", "refresh_token"] for token in login_data)

    create_client.headers["access_token"] = login_data.get("access_token")

    # проверка прав доступа
    access_token = create_client.headers.get("access_token")
    protected_responce: Response = await create_client.get(
        url="/auth/protected",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert protected_responce.status_code == status_code
    assert protected_responce.json().get("status") == "success"

    refresh_token = create_client.cookies.get("refresh_token")

    # выход из аккаунта
    auth_responce: Response = await create_client.post(
        url="/auth/logout",
        json={"refresh_token": refresh_token},
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert auth_responce.status_code == 200

    info_token = await get_redis_client_fixture.validation_token(jti=refresh_token)

    assert not info_token
