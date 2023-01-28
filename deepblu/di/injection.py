import inspect
from functools import wraps
from typing import Any, Callable

from deepblu.di.registry import (
    AnyBinding,
    AnyProvider,
    Provider,
    ProviderRegistry,
    TValue,
)

__all__ = ["bind", "bind_all", "get", "inject"]

registry = ProviderRegistry()


def bind(interface: Provider[TValue], impl: Provider[TValue]) -> None:
    """Bind an interface to an implementation.

    Args:
        interface: The interface to bind.
        impl: The implementation to bind to the given interface.

    Examples:
        >>> di.bind(DummyInterface, DummyImpl)
        >>> di.bind(OtherDummyInterface, dummy_factory)
    """
    registry[interface] = impl


def add(provider: Provider[TValue]) -> None:
    """Add a provider to the registry.

    Args:
        provider: The provider to add to the registry, bound to itself.

    Examples:
        >>> di.add(DummyImpl)
    """
    bind(provider, provider)


def bind_all(*providers: AnyBinding | AnyProvider) -> None:
    """Bind multiple interfaces to implementations.

    Args:
        providers: A list of Binding tuples of the
        form ```(interface, implementation)```.

    Examples:
        >>> di.bind_all(
                (DummyInterface, DummyImpl), (OtherDummyInterface, dummy_factory)
            )
    """
    for provider in providers:
        if isinstance(provider, tuple):
            interface, impl = provider
        else:
            interface, impl = provider, provider
        bind(interface, impl)


def get(interface: Provider[TValue]) -> TValue:
    """Get the implementation for an interface.

    Args:
        interface: The interface to get the implementation instance for.

    Returns:
        The implementation instance for the given interface.

    Examples:
        >>> dummy_instance: DummyInterface = di.get(DummyInterface)
        >>> other_dummy_instance: OtherDummyInterface = di.get(OtherDummyInterface)
    """
    return registry[interface]()


def inject(func: Provider[TValue]) -> Callable[..., TValue]:
    """Inject dependencies into a function class init.

    Args:
        params: A dictionary of parameters to inject.
        The keys are the names of the parameters and the values are the
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> TValue:
        annotations = inspect.getfullargspec(func).annotations
        for k, v in annotations.items():
            if v in registry.bindings and k not in kwargs:
                kwargs[k] = registry.bindings[v]()
        return func(*args, **kwargs)

    return wrapper
