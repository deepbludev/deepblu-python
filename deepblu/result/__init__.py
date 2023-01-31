from functools import wraps
from typing import Any, Callable, Generic, Optional, ParamSpec, TypeVar, cast

TValue = TypeVar("TValue")
TError = TypeVar("TError", bound=Exception)


class Result(Generic[TValue, TError]):
    """Represents a monadic result of a function that can be either ok or error."""

    __slots__ = ("__value", "__error", "__is_ok")
    __value: Optional[TValue]
    __error: Optional[TError]
    __is_ok: bool

    def __init__(
        self, value: Optional[TValue], error: Optional[TError], is_ok: bool = True
    ):
        if is_ok and error is not None:
            raise ValueError("Result cannot be both ok and error")
        self.__value = value
        self.__error = error
        self.__is_ok = is_ok

    def __repr__(self) -> str:
        return f"Ok({self.__value})" if self.is_ok else f"Error({self.__error})"

    def __eq_result__(self, other: "Result[TValue, TError]") -> bool:
        """Checks if the result is equal to another result.

        Used internally by __eq__.
        Equality is checked by comparing the value and the error.
        """
        is_equal_error = (
            self.error is not None
            and other.error is not None
            and type(self.error) is type(other.error)
            and self.error.args == other.error.args
        ) or self.error == other.error

        is_equal_value = self.value == other.value
        return is_equal_value and is_equal_error

    def __eq__(self, other: Any) -> bool:
        """Checks if the result is equal to another result or a value.

        Equality is checked by comparing the value and the error.
        """
        return isinstance(other, Result) and self.__eq_result__(
            cast(Result[TValue, Any], other)
        )

    @property
    def value(self) -> Optional[TValue]:
        """Returns the value of the result.

        If the result is an error, it will return None.
        """
        return self.__value

    @property
    def error(self) -> Optional[TError]:
        """Returns the error of the result.

        If the result is ok, it will return None."""
        return self.__error

    @property
    def is_ok(self) -> bool:
        """Returns True if the result is ok, False if it is an error."""
        return self.__is_ok

    @property
    def is_error(self) -> bool:
        """Returns True if the result is an error, False if it is ok."""
        return not self.is_ok

    @classmethod
    def ok(cls, value: Optional[TValue] = None) -> "Result[TValue,Any]":
        """Creates an ok result with the given value."""
        return cls(value=value, error=None)

    @classmethod
    def err(cls, error: Optional[TError] = None) -> "Result[Any, TError]":
        """Creates an error result with the given error."""
        return cls(value=None, is_ok=False, error=error)


def ok(value: Optional[TValue] = None) -> Result[TValue, Any]:
    """Creates an ok result."""
    return Result.ok(value)


def error(error: Optional[TError] | str = None) -> Result[Any, TError | Exception]:
    """Creates an error result.

    If the error is a string, it will be converted to an Exception.
    """
    return Result.err(Exception(error) if isinstance(error, str) else error)


# Used for getting the type of kwargs in a monadic function
P = ParamSpec("P")


def monadic(func: Callable[P, TValue]) -> Callable[P, Result[TValue, Any]]:
    """Decorator for monadic functions.

    Converts a function that can raise an exception into a function that returns a Result.
    """

    @wraps(func)
    def decorator(*args: P.args, **kwargs: P.kwargs) -> Result[TValue, Any]:
        try:
            return ok(func(*args, **kwargs))
        except Exception as e:
            return error(e)

    return decorator
