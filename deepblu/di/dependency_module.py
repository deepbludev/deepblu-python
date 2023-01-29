from .registry import AnyBinding, AnyProvider


class DependencyModule:
    imports: list["DependencyModule"]
    providers: list[AnyBinding | AnyProvider]
