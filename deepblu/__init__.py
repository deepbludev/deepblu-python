"""
deepblu
======================

Library for advanced architectures/patterns in modern Python.
Domain-Driven Design (DDD), CQRS, Event Sourcing, Event-driven architectures, message queues, unit of work, dependency injection and more.
"""

from .di import hello_di

__version__ = "0.1.0"


def hello() -> str:
    """
    Hello

    Get a greeting message from deepblu package.

    :return: a greeting message from deepblu
    :rtype: str
    """
    return "Hello, deepblu!"


__all__ = ["hello", "hello_di"]
