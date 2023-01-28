import abc
from typing import Awaitable, Callable, Generic, TypeVar

import pytest
from pydantic import BaseModel

from deepblu import di


class User:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name


E = TypeVar("E")


class CreateUserRequest(BaseModel):
    id: str
    name: str


class Repo(Generic[E], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def get(self, id: str) -> E:
        pass

    @abc.abstractmethod
    async def save(self, entity: E) -> None:
        pass


class UserSQLRepo(Repo[User]):
    async def get(self, id: str) -> User:
        return User(id, "John")

    async def save(self, entity: User) -> None:
        print(f"Saving user {entity.id} to SQL")
        pass


TUseCaseResult = TypeVar("TUseCaseResult")
TUseCaseRequest = TypeVar("TUseCaseRequest")


class UseCase(Generic[TUseCaseRequest, TUseCaseResult], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def run(self, dto: TUseCaseRequest) -> TUseCaseResult:
        pass


class CreateUser(UseCase[CreateUserRequest, User]):
    @di.inject
    def __init__(self, repo: Repo[User]) -> None:
        self.repo = repo

    async def run(self, dto: CreateUserRequest) -> User:
        user = User(**dto.dict())
        await self.repo.save(user)
        return user


UseCaseFn = Callable[[TUseCaseRequest], Awaitable[TUseCaseResult]]


@di.inject
def create_user_usecase(repo: Repo[User]) -> UseCaseFn[CreateUserRequest, User]:
    async def run(dto: CreateUserRequest) -> User:
        user = User(**dto.dict())
        await repo.save(user)
        return user

    return run


class UserService:
    @di.inject
    def __init__(self, repo: Repo[User], create_user_usecase: CreateUser) -> None:
        self.repo = repo
        self.create_user_usecase = create_user_usecase

    async def create_user(self, dto: CreateUserRequest) -> User:
        user = await self.create_user_usecase.run(dto)
        await self.repo.save(user)
        return user

    async def get_user(self, id: str) -> User:
        return await self.repo.get(id)

    async def save_user(self, user: User) -> None:
        await self.repo.save(user)


class APIKey:
    def __init__(self, key: str) -> None:
        self.key = key


def api_key_factory() -> APIKey:
    return APIKey("some-random-apikey")


class UserController:
    @di.inject
    def __init__(self, service: UserService, api_key: APIKey) -> None:
        self.service = service
        self.api_key = api_key.key

    async def get_user(self, id: str) -> User:
        return await self.service.get_user(id)

    async def save_user(self, user: User) -> None:
        await self.service.save_user(user)


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