from typing import Any, Callable, TypeVar

TValue = TypeVar("TValue")
TProvider = Callable[..., TValue]
AnyProvider = TProvider[Any]
TBinding = tuple[TProvider[TValue], TProvider[TValue]]
AnyBinding = tuple[AnyProvider, AnyProvider]


class ProviderRegistry:
    __slots__ = "__bindings__"
    __bindings__: dict[AnyProvider, AnyProvider]

    def __init__(self) -> None:
        self.__bindings__ = {}

    def bind(  # type: ignore
        self, interface: TProvider[TValue], impl=TProvider[TValue]  # type: ignore
    ) -> "ProviderRegistry":
        self.__bindings__[interface] = impl
        return self

    def __setitem__(
        self, interface: TProvider[TValue], impl: TProvider[TValue]
    ) -> "ProviderRegistry":
        return self.bind(interface, impl)

    def get(self, interface: TProvider[TValue]) -> TProvider[TValue]:
        return self.__bindings__[interface]

    def __getitem__(self, interface: TProvider[TValue]) -> TProvider[TValue]:
        return self.get(interface)

    @property
    def bindings(self) -> dict[AnyProvider, AnyProvider]:
        """Get current bindings"""
        return self.__bindings__
