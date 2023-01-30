from abc import ABC
from typing import Callable

from deepblu.di import injection
from deepblu.di.registry import AnyBinding, AnyProvider, Provider, TProviderValue


class Module(ABC):
    submodules: list[type["Module"]] = []
    providers: list[AnyBinding | AnyProvider] = []

    def get(self, interface: Provider[TProviderValue]) -> TProviderValue:
        return injection.get(interface)


def module(
    submodules: list[type[Module]] = [],
    providers: list[AnyBinding | AnyProvider] = [],
) -> Callable[[type[Module]], type[Module]]:
    def wrapper(cls: type[Module]) -> type[Module]:
        cls.submodules = submodules
        cls.providers = providers
        injection.bind_all(*providers)
        return cls

    return wrapper
