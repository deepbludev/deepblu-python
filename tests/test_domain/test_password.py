import pytest
from pydantic import ValidationError

from deepblu.domain import Schema
from deepblu.domain.vo import PasswordStr


class UserMock(Schema):
    password: PasswordStr


class CustomPassword(PasswordStr):
    min_length = 10


def test_password_fails_with_less_than_8_chars() -> None:
    with pytest.raises(ValidationError):
        UserMock(password="1234567")


def test_creates_correctly() -> None:
    user = UserMock(password=PasswordStr("12345678"))
    assert isinstance(user.password, PasswordStr)
    assert user.password.hashed != "12345678"


def test_fails_hashing_invalid_password() -> None:
    with pytest.raises(ValidationError):
        CustomPassword.hash("123456789")


def test_verify_password() -> None:
    password = PasswordStr("12345678")
    hashed = password.hashed

    assert PasswordStr.verify(password, hashed)
    assert password.compare(hashed)


def test_is_valid() -> None:
    assert PasswordStr.is_valid("12345678")
    assert not PasswordStr.is_valid("1234567")


def test_monadic_parse() -> None:
    assert PasswordStr.monadic_parse("12345678").is_ok
    assert PasswordStr.monadic_parse("1234567").is_error
