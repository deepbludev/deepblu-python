from abc import ABC
from typing import Callable

from deepblu.di import injection as di
from deepblu.di.registry import AnyBinding, AnyProvider, Provider, TProviderValue


class Module(ABC):
    imports: list[type["Module"]] = []
    providers: list[AnyBinding | AnyProvider] = []
    exports: list[AnyBinding | AnyProvider] = []

    def get(self, interface: Provider[TProviderValue]) -> TProviderValue:
        """Returns an instance of the given interface, if it is bound in the module."""
        # TODO: Return instance only if it is bound in the module or in a submodule
        return di.get(interface)


def module(
    imports: list[type[Module]] = [],
    providers: list[AnyBinding | AnyProvider] = [],
    exports: list[AnyBinding | AnyProvider] = [],
) -> Callable[[type[Module]], type[Module]]:
    """Decorator that binds the given providers and submodules to the module."""

    def wrapper(cls: type[Module]) -> type[Module]:
        cls.imports = imports
        cls.providers = providers
        cls.exports = exports

        di.bind_all(*providers)
        return cls

    return wrapper
