import inspect
from abc import ABC
from functools import wraps
from typing import Any, Callable, TypeVar, cast

TProviderValue = TypeVar("TProviderValue")
Provider = Callable[..., TProviderValue]
AnyProvider = Provider[Any]
Binding = tuple[Provider[TProviderValue], Provider[TProviderValue]]
AnyBinding = tuple[AnyProvider, AnyProvider]


class ProviderRegistry:
    """Provider registry for dependency injection.

    Used only as a singleton instance called `registry`, exported by the `di` module.

    ```py title="Example:"
    from deepblu.di import registry

    registry.bind(Interface, Implementation)
    registry[OtherInterface] = OtherImplementation

    isinstance(registry[Interface], Implementation) # True
    isinstance(registry.get(OtherInterface), OtherImplementation) # True

    registry.bindings
    # {Interface: Implementation, OtherInterface: OtherImplementation}

    ```
    """

    __slots__ = ("__bindings__", "__instances__")
    __bindings__: dict[AnyProvider, AnyProvider]
    __instances__: dict[AnyProvider, Any]

    def __init__(self) -> None:
        self.__bindings__ = {}
        self.__instances__ = {}

    def bind(
        self, interface: Provider[TProviderValue], impl: Provider[TProviderValue]
    ) -> "ProviderRegistry":
        """Bind an interface to an implementation."""
        self.__bindings__[interface] = impl
        return self

    def __setitem__(
        self, interface: Provider[TProviderValue], impl: Provider[TProviderValue]
    ) -> "ProviderRegistry":
        """Bind an interface to an implementation."""
        return self.bind(interface, impl)

    def get(self, interface: Provider[TProviderValue]) -> TProviderValue:
        """Get the implementation instance for an interface."""
        try:
            instance = self.__instances__[interface]
        except KeyError:
            instance = self.__bindings__[interface]()
        self.__instances__[interface] = instance
        return cast(TProviderValue, instance)

    def __getitem__(self, interface: Provider[TProviderValue]) -> TProviderValue:
        """Get the implementation instance for an interface.""" ""
        return self.get(interface)

    @property
    def bindings(self) -> dict[AnyProvider, AnyProvider]:
        """Get current bindings"""
        return self.__bindings__


# Provider registry instance for dependency injection.
registry = ProviderRegistry()


def bind(interface: Provider[TProviderValue], impl: Provider[TProviderValue]) -> None:
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


def add(provider: Provider[TProviderValue]) -> None:
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


def get(interface: Provider[TProviderValue]) -> TProviderValue:
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


def provide_many(interface: AnyProvider, impls: list[AnyProvider]) -> AnyBinding:
    """Get a list of providers for a list of interfaces.

    Args:
        interface: The interface to get the implementation instances for.
        impls: A list of providers to get the implementation instances for.
    Returns:
        A binding of the interface and a list of providers.

    ```py title="Example:" linenums="1"
    @di.module(providers=[
        di.provide_many(list[DummyInterface], [DummyImpl, OtherDummyImpl])
    ])
    ```
    """
    return (interface, lambda: [provider() for provider in impls])


def inject(func: Provider[TProviderValue]) -> Callable[..., TProviderValue]:
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
    def wrapper(*args: Any, **kwargs: Any) -> TProviderValue:
        annotations = inspect.getfullargspec(func).annotations
        for name, provider in annotations.items():
            if provider in registry.bindings and name not in kwargs:
                kwargs[name] = registry[provider]
        return func(*args, **kwargs)

    return wrapper


def injectable(cls: Provider[TProviderValue]) -> Provider[TProviderValue]:
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


ProviderList = list[AnyBinding | AnyProvider]


class Module(ABC):
    """
    A module is a collection of providers and imported submodules.

    It is used to organize the providers in a hierarchical way, and to
    provide a way to bind providers to the dependency injection container.

    A module can be imported by other modules, and its providers will be
    bound to the container when the module is imported, if the module class
    is decorated with the `module` decorator.
    """

    imports: list[type["Module"]]
    providers: ProviderList

    def get(self, interface: Provider[TProviderValue]) -> TProviderValue:
        """
        Returns an instance of the given interface.

        It is used to avoid the need to import the di container when using
        module-based dependency injection.
        """

        return get(interface)


def module(
    imports: list[type[Module]] | None = None,
    providers: ProviderList | None = None,
) -> Callable[[type[Module]], type[Module]]:
    """
    Decorator that binds the given providers and submodules to the module.

    The providers are bound to the di container when the module is imported.
    The submodules are imported when the module is imported, binding their own
    providers to the di container.  This is useful to organize the providers in
    a hierarchical way.

    """

    def wrapper(cls: type[Module]) -> type[Module]:
        cls.imports = imports or []
        cls.providers = providers or []

        bind_all(*cls.providers)
        return cls

    return wrapper
