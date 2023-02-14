from abc import ABC
from typing import Callable

from deepblu.di import injection as di
from deepblu.di.registry import AnyBinding, AnyProvider, Provider, TProviderValue

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

        return di.get(interface)


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

        di.bind_all(*cls.providers)
        return cls

    return wrapper
