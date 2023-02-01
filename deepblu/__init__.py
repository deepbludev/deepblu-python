"""
deepblu
======================

Library for advanced architectures/patterns in modern Python.
Domain-Driven Design (DDD), CQRS, Event Sourcing, Event-driven architectures, message queues, unit of work, dependency injection and more.
"""

from .di import (
    Module,
    add,
    bind,
    get,
    inject,
    injectable,
    module,
    provide_many,
    registry,
)
from .result import Result, error, monadic, ok

__version__ = "0.2.0"

__all__ = [
    # di
    "Module",
    "add",
    "bind",
    "get",
    "inject",
    "injectable",
    "module",
    "provide_many",
    "registry",
    # result
    "Result",
    "error",
    "monadic",
    "monadic_async",
    "ok",
]
