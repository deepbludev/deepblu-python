from typing import Optional

import pytest

from deepblu.result import Result, error, monadic, monadic_async, ok


@pytest.mark.parametrize("value", ["test", None])
def test_result_is_ok_when_value_is_not_none(value: str) -> None:
    result = ok(value)
    assert result.is_ok
    assert result == Result.ok(value)
    assert result.value == value
    assert not result.is_error
    assert result.error is None
    assert repr(result) == f"Ok({value})"


@pytest.mark.parametrize("err", [Exception("test"), None, ValueError("test"), "test"])
def test_result_is_error_when_value_is_none(err: Optional[Exception | str]) -> None:
    result = error(err)
    assert result.is_error
    assert result.error == err if isinstance(err, Exception) else Exception(err)
    assert not result.is_ok
    assert result.value is None
    assert repr(result) == f"Error({err})"


def test_creates_error_with_exceptions() -> None:
    result = error(ValueError("test"))
    assert result.is_error
    assert isinstance(result.error, ValueError)
    assert result.error.args == ("test",)
    assert not result.is_ok
    assert result.value is None


@pytest.mark.parametrize("error", [ValueError("test"), Exception("test")])
def test_fails_when_created_with_value_and_error(error: Exception) -> None:
    with pytest.raises(ValueError):
        Result(value="test", error=error)


@pytest.mark.parametrize("value", ["test", None])
def test_result_eq(
    value: Optional[str],
) -> None:
    assert ok() == ok()
    assert ok(value) == ok(value)
    assert ok(value) != value
    assert ok(value) != ok("other test")

    assert error() == error()
    assert error(value) == error(value)
    assert error(Exception(value)) == error(Exception(value))
    assert error(Exception(value or "")) == error(value or "")
    assert error(Exception(value)) != Exception(value)
    assert error(Exception(value)) != error("other test")
    assert error(value) != error("other test")


def test_is_eq_to_other_result_with_different_value_or_error() -> None:
    assert ok("test") != ok("test2")
    assert error("test") != error("test2")


def test_monadic_as_hof() -> None:
    def lowercase_str(input: str) -> str:
        if not input:
            raise ValueError("Cannot lowercase empty string")
        return input.lower()

    assert monadic(lowercase_str)("TEST") == ok("test")
    assert monadic(lowercase_str)("") == error(
        ValueError("Cannot lowercase empty string")
    )
    assert lowercase_str("TEST") == "test"
    with pytest.raises(ValueError):
        lowercase_str("")


def test_monadic_as_decorator() -> None:
    @monadic
    def capitalize_str(input: str) -> str:
        if not input:
            raise ValueError("Cannot capitalize empty string")
        return input.capitalize()

    assert capitalize_str("test") == ok("Test")
    assert capitalize_str("") == error(ValueError("Cannot capitalize empty string"))


@pytest.mark.asyncio
async def test_monadic_async_as_decorator() -> None:
    @monadic_async
    async def capitalize_str(input: str) -> str:
        if not input:
            raise ValueError("Cannot capitalize empty string")
        return input.capitalize()

    assert await capitalize_str("test") == ok("Test")
    assert await capitalize_str("") == error(
        ValueError("Cannot capitalize empty string")
    )
