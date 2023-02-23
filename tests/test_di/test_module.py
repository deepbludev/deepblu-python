from typing import cast

import pytest

from deepblu import di
from deepblu.di import Provider
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


@di.module(providers=[di.injectable(UserController)])
class DummyModule(di.Module):
    pass


usecases: list[Provider[AnyUseCase]] = [CreateUser, GetUser]


@di.module(providers=[CommandBus])
class CQRSModule(di.Module):
    pass


@di.module(
    imports=[DummyModule],
    providers=[
        di.provide_many(list[AnyUseCase], usecases),
        (Repo[User], UserSQLRepo),
        UserService,
    ],
)
class UserModule(di.Module):
    pass


@di.module(imports=[UserModule, CQRSModule])
class AppModule(di.Module):
    pass


def test_module() -> None:
    dummy_module = DummyModule()
    assert di.Module is not None
    assert DummyModule._providers == [UserController]
    assert dummy_module._providers == [UserController]


@pytest.fixture(scope="module")
def user_module() -> di.Module:
    return UserModule()


@pytest.fixture(scope="module")
def app_module() -> di.Module:
    return AppModule()


def test_user_module(user_module: di.Module) -> None:
    assert len(UserModule._providers) == 3
    assert len(user_module._providers) == 3
    assert UserModule._imports == [DummyModule]
    assert user_module._imports == [DummyModule]


@pytest.mark.asyncio
async def test_decorator_injects_providers(
    user_module: di.Module, app_module: di.Module
) -> None:
    commandbus = app_module.get(CommandBus)
    assert len(commandbus.usecases) == 2
    assert app_module._imports == [UserModule, CQRSModule]

    assert isinstance(app_module.get(Repo[User]), UserSQLRepo)

    commandbus_create_user = cast(CreateUser, commandbus.usecases[0])
    user = await commandbus_create_user.run(CreateUserDTO(id="2", name="Jack"))
    assert user.name == "Jack"

    assert isinstance(di.get(UserController), UserController)
    assert isinstance(user_module.get(UserController), UserController)
