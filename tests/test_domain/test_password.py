import pytest
from pydantic import ValidationError

from deepblu.domain import Schema
from deepblu.domain.vo import Password


class UserMock(Schema):
    password: Password


class CustomPassword(Password):
    min_length = 10


def test_password_fails_with_less_than_8_chars() -> None:
    with pytest.raises(ValidationError):
        UserMock(password="1234567")


def test_creates_correctly() -> None:
    user = UserMock(password=Password("12345678"))
    assert isinstance(user.password, Password)
    assert user.password.encrypt() != "12345678"


def test_fails_hashing_invalid_password() -> None:
    with pytest.raises(ValidationError):
        CustomPassword.hash("123456789")


def test_verify_password() -> None:
    password = Password("12345678")
    hashed = password.encrypt()

    assert Password.verify(password, hashed)
    assert password.compare(hashed)


def test_is_valid() -> None:
    assert Password.is_valid("12345678")
    assert not Password.is_valid("1234567")
