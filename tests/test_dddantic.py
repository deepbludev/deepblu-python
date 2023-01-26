import dddantic


def test_dddantic_module_is_defined() -> None:
    assert dddantic is not None
    assert dddantic.__version__ == "0.1.0"
