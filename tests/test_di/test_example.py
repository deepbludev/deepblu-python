import pytest

from deepblu import di
from examples.di import (
    APIKey,
    CreateUser,
    CreateUserRequest,
    Repo,
    User,
    UserController,
    UserService,
    UserSQLRepo,
    api_key_factory,
    create_user_usecase,
)


@pytest.fixture
def bind_all() -> None:
    di.bind(APIKey, api_key_factory)
    di.add(UserController)
    di.bind_all(
        CreateUser,
        create_user_usecase,
        UserService,
        (Repo[User], UserSQLRepo),
    )


@pytest.mark.asyncio
async def test_inject(bind_all: None) -> None:
    service = UserService()
    user = await service.get_user("1")
    assert user.name == "John"

    api_key = di.get(APIKey)
    assert api_key.key == "some-random-apikey"

    ctrl = UserController()
    user = await ctrl.get_user("1")
    assert user.name == "John"
    assert ctrl.api_key == "some-random-apikey"

    create_user = CreateUser()
    user = await create_user.run(CreateUserRequest(id="1", name="John"))
    assert user.name == "John"

    create_user_fn = create_user_usecase()
    user = await create_user_fn(CreateUserRequest(id="1", name="John"))
    assert user.name == "John"


@pytest.mark.asyncio
async def test_manual_inject() -> None:
    repo = UserSQLRepo()
    create_user = CreateUser(repo=repo)
    user = await create_user.run(CreateUserRequest(id="1", name="John"))
    assert user.name == "John"
