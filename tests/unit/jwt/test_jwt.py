import pytest
import uuid

from src.auth.utils.jwt.jwt_manager import JwtToken
from src.auth.schemas.user import UserResponceSchema


@pytest.mark.parametrize(
    "user_id, email, role",
    [
        (uuid.uuid4(), "mgkr@mail.ru", "user"),
        (uuid.uuid4(), "testemail@mail.ru", "admin"),
        (bool, "usermail@gmail.com", "user"),
    ],
)
def test_create_access_jwt_token(user_id, email, role):
    jwt_token = JwtToken.create_access_jwt_token(user_id, email, role)

    assert jwt_token


def test_create_refresh_jwt_token():
    refresh_token = JwtToken.create_refresh_jwt_token()

    assert refresh_token


def test_issuing_tokens():
    user_data = UserResponceSchema(
        id=uuid.uuid4(), role="user", email="testmail@mail.ru"
    )
    tokens: tuple[str, str] = JwtToken.issuing_tokens(
        user_data=user_data,
    )

    assert isinstance(tokens, tuple)
    assert len(tokens) == 2


def test_decode_jwt_token():
    user_data = {"id": uuid.uuid4(), "email": "mgkr@mail.ru", "role": "user"}
    access_token = JwtToken.create_access_jwt_token(
        user_id=user_data.get("id"),
        email=user_data.get("email"),
        role=user_data.get("role"),
    )

    assert access_token

    decode_access_token = JwtToken.decode_jwt_token(token=access_token)

    assert decode_access_token
    assert decode_access_token.email == user_data.get("email")
    assert decode_access_token.sub == user_data.get("id")
    assert decode_access_token.role == user_data.get("role")
