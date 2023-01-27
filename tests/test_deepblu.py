import deepblu


def test_deepblu_module_is_defined() -> None:
    assert deepblu is not None
    assert deepblu.__version__ == "0.1.0"
    assert deepblu.hello() == "Hello, deepblu!"
