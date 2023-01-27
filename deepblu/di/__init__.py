"""
Dependency Injection
======================

This module provides a simple dependency injection framework, based on a registry of bindings between interfaces and their
implementations. Interfaces are classes (typically abstract) and implementations are concrete subclasses or
factory functions that return a value of the same type as the Interface.
Example:
    ```python
    class DummyInterface(ABC):
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


    di.bind(DummyInterface, DummyImpl)
    di.bind(OtherDummyInterface, dummy_factory)
    ## Equivalent to:
    # di.bind_all((DummyInterface, DummyImpl), (OtherDummyInterface, dummy_factory))

    dummy_instance = di.get(DummyInterface)()
    other_dummy_instance = di.get(OtherDummyInterface)()

    >>> di.get(DummyInterface)
    # DummyImpl

    >>> dummy_instance.foo()
    # "foo"

    >>> di.get(OtherDummyInterface)
    # <function dummy_factory at 0x7f9b1c0b0d30>

    >>> other_dummy_instance.bar()
    # "bar"
    ```
"""


from deepblu.di.registry import AnyBinding, ProviderRegistry, TProvider, TValue

__all__ = ["bind", "bind_all", "get"]

registry = ProviderRegistry()


def bind(interface: TProvider[TValue], impl: TProvider[TValue]) -> None:
    """Bind an interface to an implementation."""
    registry[interface] = impl


def bind_all(*providers: AnyBinding) -> None:
    """Bind multiple interfaces to implementations."""
    for interface, impl in providers:
        bind(interface, impl)


def get(interface: TProvider[TValue]) -> TProvider[TValue]:
    """Get the implementation for an interface."""
    return registry[interface]
