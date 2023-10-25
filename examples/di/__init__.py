from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Generic, TypeVar

from pydantic import BaseModel

from deepblu import di


class User:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name


E = TypeVar("E")


class Repo(Generic[E], ABC):
    @abstractmethod
    async def get(self, id: str) -> E:
        pass

    @abstractmethod
    async def save(self, entity: E) -> None:
        pass


class UserSQLRepo(Repo[User]):
    async def get(self, id: str) -> User:
        return User(id, "John")

    async def save(self, entity: User) -> None:
        print(f"Saving user {entity.id} to SQL")


TUseCaseResult = TypeVar("TUseCaseResult")
TUseCaseDTO = TypeVar("TUseCaseDTO")


class UseCase(Generic[TUseCaseDTO, TUseCaseResult], ABC):
    @abstractmethod
    async def run(self, dto: TUseCaseDTO) -> TUseCaseResult:
        pass


AnyUseCase = UseCase[Any, Any]


class CreateUserDTO(BaseModel):
    id: str
    name: str


class CreateUser(UseCase[CreateUserDTO, User]):
    @di.inject
    def __init__(self, repo: Repo[User]) -> None:
        self.repo = repo

    async def run(self, dto: CreateUserDTO) -> User:
        user = User(**dto.dict())
        await self.repo.save(user)
        return user


class GetUserDTO(BaseModel):
    id: str


class GetUser(UseCase[GetUserDTO, User]):
    @di.inject
    def __init__(self, repo: Repo[User]) -> None:
        self.repo = repo

    async def run(self, dto: GetUserDTO) -> User:
        return await self.repo.get(dto.id)


UseCaseFn = Callable[[TUseCaseDTO], Awaitable[TUseCaseResult]]


@di.inject
def create_user_usecase(repo: Repo[User]) -> UseCaseFn[CreateUserDTO, User]:
    async def run(dto: CreateUserDTO) -> User:
        user = User(**dto.dict())
        await repo.save(user)
        return user

    return run


@di.injectable
class UserService:
    def __init__(self, repo: Repo[User], create_user_usecase: CreateUser) -> None:
        self.repo = repo
        self.create_user_usecase = create_user_usecase

    async def create_user(self, dto: CreateUserDTO) -> User:
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


# No decorator needed
class UserController:
    def __init__(self, service: UserService, api_key: APIKey) -> None:
        self.service = service
        self.api_key = api_key.key

    async def get_user(self, id: str) -> User:
        return await self.service.get_user(id)

    async def save_user(self, user: User) -> None:
        await self.service.save_user(user)


# Injecting lists of dependencies
class CommandBus:
    usecases: list[AnyUseCase]

    @di.inject
    def __init__(self, usecases: list[AnyUseCase]) -> None:
        self.usecases = usecases
