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

registry = ProviderRegistry()


def bind(interface: Provider[TValue], impl: Provider[TValue]) -> None:
    """Bind an interface to an implementation.

     Args:
         interface: The interface to bind.
         impl: The implementation to bind to the given interface.

    ```py title="Example:" linenums="1"
     di.bind(DummyInterface, DummyImpl)
     di.bind(OtherDummyInterface, dummy_factory)
    ```
    """
    registry[interface] = impl


def add(provider: Provider[TValue]) -> None:
    """Add a provider to the registry.

    Args:
        provider: The provider to add to the registry, bound to itself.

    ```py title="Example:" linenums="1"
    di.add(DummyImpl)
    ```
    """
    bind(provider, provider)


def bind_all(*providers: AnyBinding | AnyProvider) -> None:
    """Bind multiple interfaces to implementations.

    Args:
        providers: A list of Binding tuples of the
        form ```(interface, implementation)```.

    ```py title="Example:" linenums="1"
    di.bind_all(
        (DummyInterface, DummyImpl), (OtherDummyInterface, dummy_factory)
    )
    ```
    """
    for provider in providers:
        if isinstance(provider, tuple):
            interface, impl = provider
        else:
            interface, impl = provider, provider
        bind(interface, impl)


def get(interface: Provider[TValue]) -> TValue:
    """Get the implementation instance for an interface.

    Args:
        interface: The interface to get the implementation instance for.

    Returns:
        The implementation instance for the given interface.

    ```py title="Example:" linenums="1"
    dummy_instance: DummyInterface = di.get(DummyInterface)
    other_dummy_instance: OtherDummyInterface = di.get(OtherDummyInterface)
    ```
    """
    return registry[interface]


def inject(func: Provider[TValue]) -> Callable[..., TValue]:
    """Decorator to inject dependencies into a function or `__init__` method.

    ```py title="Example:" linenums="1"
    class DummyClass:
        @di.inject
        def __init__(self, dummy: DummyInterface):
            self.dummy = dummy
    ```

    ```py title="Example:" linenums="1"
    @di.inject
    def print_dummy(dummy: DummyInterface):
        print(repr(dummy))
    ```
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> TValue:
        annotations = inspect.getfullargspec(func).annotations
        for k, v in annotations.items():
            if v in registry.bindings and k not in kwargs:
                kwargs[k] = registry.bindings[v]()
        return func(*args, **kwargs)

    return wrapper


def injectable(cls: Provider[TValue]) -> Provider[TValue]:
    """Inject dependencies into a class `__init__`.

    Args:
        cls: The class to inject dependencies into.

    ```py title="Example:" linenums="1"
    @di.injectable
    class DummyClass:
        def __init__(self, dummy: DummyInterface):
            self.dummy = dummy
    ```
    ```py title="Example:" linenums="1"
    class DummyClass:
        def __init__(self, dummy: DummyInterface):
            self.dummy = dummy

    di.add(di.injectable(DummyClass)) # avoids decorator syntax
    ```
    """
    cls.__init__ = inject(cls.__init__)  # type: ignore
    return cls
