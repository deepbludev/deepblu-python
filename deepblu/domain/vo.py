from typing import TypeVar

from passlib.hash import bcrypt
from pydantic import ConstrainedStr

from deepblu.domain import Primitive

TPassword = TypeVar("TPassword", bound="Password")


class Password(ConstrainedStr, Primitive):
    """
    Password value object. It is a string with a minimum length of 8 characters.
    It extends `ConstrainedStr`, so it can be used as a type annotation.
    For further customization, you can extend this class and override the
    `ConstrainedStr` attributes.

    Usage:
    ```python
    from deepblu import Schema # or from pydantic import BaseModel
    from deepblu.domain.vo import Password

    class User(Schema):
        password: Password

    User(password="1234567")  # raises ValidationError
    User(password="12345678") # ok

    print(user.password) # prints "12345678"
    isinstance(user.password, Password) # True
    isinstance(user.password, str) # True

    hashed = Password.hash("1234567") # raises ValidationError
    hashed = Password.hash("12345678")
    # $2b$12$R1Uej9/bZSO/VCQ0e9PR6etdreVaDQqBqVA0rvuKiBwfAuxQG/9.q

    Password("12345678").compare(hashed) # True
    Password("abcdefghi").compare(hashed) # False
    Password.verify("12345678", hashed) # True
    Password.verify("abcdefghi", hashed) # False



    class CustomPassword(Password):
        min_length = 10

    CustomPassword.hash("123456789") # raises ValidationError

    ```
    """

    __encrypter = bcrypt
    min_length = 8

    @classmethod
    def hash(cls: type[TPassword], password: str) -> str:
        hashed: str = cls.__encrypter.hash(cls.parse(password))
        return hashed

    def encrypt(self) -> str:
        return Password.hash(self)

    @classmethod
    def verify(cls, plain: str, hashed: str) -> bool:
        return True if cls.__encrypter.verify(plain, hashed) else False

    def compare(self, hashed: str) -> bool:
        return Password.verify(self, hashed)
