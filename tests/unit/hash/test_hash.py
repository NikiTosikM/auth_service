import pytest

from src.auth.utils.hash_password.hashing import hashing


@pytest.mark.parametrize(
    "data",
    [
        ("123456"),
        ("Nameuser!%efkwkfkdgs"),
        (""),
    ],
)
def test_create_hash(data):
    hash = hashing.create_hash(data)

    assert hash


@pytest.mark.parametrize(
    "data, result_verification",
    [("123456", True), ("Nameuser!%efkwkfkdgs", True), ("", True)],
)
def test_create_and_verification_hash(data, result_verification):
    hash = hashing.create_hash(data)
    assert hash

    verification: bool = hashing.hash_verification(data, hash)
    assert result_verification == verification
