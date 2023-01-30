from typing import cast

import pytest

from deepblu import di
from examples.di import (
    AnyUseCase,
    APIKey,
    CommandBus,
    CreateUser,
    CreateUserDTO,
    GetUser,
    Repo,
    User,
    UserController,
    UserService,
    UserSQLRepo,
    api_key_factory,
    create_user_usecase,
)


@pytest.fixture(scope="module")
def bind_all() -> None:
    di.bind(APIKey, api_key_factory)
    di.add(UserService)
    di.bind_all(
        CreateUser,
        create_user_usecase,
        di.injectable(UserController),  # No decorator needed
        (Repo[User], UserSQLRepo),
        CommandBus,
        # injecting multiple providers of a type
        di.provide_many(list[AnyUseCase], [CreateUser, GetUser]),
    )


@pytest.mark.asyncio
async def test_inject(bind_all: None) -> None:
    service = UserService()  # type: ignore
    user = await service.get_user("1")
    assert user.name == "John"

    api_key = di.get(APIKey)
    assert api_key.key == "some-random-apikey"

    ctrl = UserController()  # type: ignore
    user = await ctrl.get_user("1")
    assert user.name == "John"
    assert ctrl.api_key == "some-random-apikey"

    create_user = CreateUser()
    user = await create_user.run(CreateUserDTO(id="1", name="John"))
    assert user.name == "John"

    create_user_fn = create_user_usecase()
    user = await create_user_fn(CreateUserDTO(id="1", name="John"))
    assert user.name == "John"

    commandbus = CommandBus()
    assert len(commandbus.usecases) == 2

    commandbus_create_user = cast(CreateUser, commandbus.usecases[0])
    user = await commandbus_create_user.run(CreateUserDTO(id="2", name="Jack"))
    assert user.name == "Jack"


@pytest.mark.asyncio
async def test_manual_inject() -> None:
    user_sql_repo = UserSQLRepo()
    create_user = CreateUser(repo=user_sql_repo)
    user = await create_user.run(CreateUserDTO(id="1", name="John"))
    assert user.name == "John"
