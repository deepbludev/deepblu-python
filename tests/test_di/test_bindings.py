import abc

import pytest

from deepblu import di


class DummyInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def foo(self) -> str:
        raise NotImplementedError


class DummyImpl(DummyInterface):
    def foo(self) -> str:
        return "foo"


class OtherDummyInterface:
    def bar(self) -> str:
        return "bar"


def dummy_factory() -> OtherDummyInterface:
    return OtherDummyInterface()


@pytest.fixture
def bind_all() -> None:
    bindings = [(DummyInterface, DummyImpl), (OtherDummyInterface, dummy_factory)]
    di.bind_all(*bindings)


def test_bind_and_get_with_class(bind_all: None) -> None:
    impl = di.get(DummyInterface)
    instance = impl()
    assert impl == DummyImpl
    assert instance.foo() == "foo"


def test_bind_and_get_with_factory(bind_all: None) -> None:
    impl = di.get(OtherDummyInterface)
    instance = impl()
    assert impl == dummy_factory
    assert instance.bar() == "bar"
