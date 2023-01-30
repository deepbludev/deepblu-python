from typing import cast

import pytest

from deepblu import di
from deepblu.di.registry import Provider
from examples.di import (
    AnyUseCase,
    CommandBus,
    CreateUser,
    CreateUserDTO,
    GetUser,
    Repo,
    User,
    UserController,
    UserService,
    UserSQLRepo,
)


class DummyModule(di.Module):
    pass


usecases: list[Provider[AnyUseCase]] = [CreateUser, GetUser]


@di.module(
    providers=[
        CommandBus,
        di.provide_many(list[AnyUseCase], usecases),
    ],
)
class CQRSModule(di.Module):
    pass


@di.module(
    imports=[DummyModule, CQRSModule],
    providers=[
        di.injectable(UserController),
        (Repo[User], UserSQLRepo),
        UserService,
    ],
)
class UserModule(di.Module):
    pass


def test_module() -> None:
    dummy_module = DummyModule()
    assert di.Module is not None
    assert DummyModule.providers == []
    assert dummy_module.providers == []


@pytest.fixture
def decorated_module() -> di.Module:
    return UserModule()


def test_decorated_module(decorated_module: di.Module) -> None:
    assert len(UserModule.providers) == 3
    assert len(decorated_module.providers) == 3
    assert UserModule.imports == [DummyModule, CQRSModule]
    assert decorated_module.imports == [DummyModule, CQRSModule]


@pytest.mark.asyncio
async def test_decorator_injects_providers(decorated_module: di.Module) -> None:
    commandbus = CommandBus()
    assert len(commandbus.usecases) == 2

    commandbus_create_user = cast(CreateUser, commandbus.usecases[0])
    user = await commandbus_create_user.run(CreateUserDTO(id="2", name="Jack"))
    assert user.name == "Jack"

    assert isinstance(di.get(UserController), UserController)
    assert isinstance(decorated_module.get(UserController), UserController)
