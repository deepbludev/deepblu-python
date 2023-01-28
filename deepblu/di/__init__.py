"""
This module provides a simple dependency injection framework, based on a registry of bindings between interfaces and their
implementations. Interfaces are classes (typically abstract) and implementations are concrete subclasses or
factory functions that return a value of the same type as the Interface.

Basic Usage:
    ```python
    class DummyInterface(ABC):
        def foo(self) -> str:
            raise NotImplementedError


    class DummyImpl(DummyInterface):
        def foo(self) -> str:
            return "foo"


    class OtherDummyInterface:
        def bar(self) -> str:
            return "bar"


    def dummy_factory() -> OtherDummyInterface:
        return OtherDummyInterface()


    di.bind(DummyInterface, DummyImpl)
    di.bind(OtherDummyInterface, dummy_factory)
    ## Equivalent to:
    # di.bind_all((DummyInterface, DummyImpl), (OtherDummyInterface, dummy_factory))

    dummy_instance: DummyInterface = di.get(DummyInterface)
    other_dummy_instance: OtherDummyInterface = di.get(OtherDummyInterface)

    >>> dummy_instance.foo()
    "foo"

    >>> other_dummy_instance.bar()
    "bar"
    ```
    **More advanced example:**
    ```python
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


    di.bind_all(
        CreateUser,
        create_user_usecase,
        UserService,
        UserController,
        (APIKey, api_key_factory)
        (Repo[User], UserSQLRepo),
    )


    ctrl: UserController = UserController() # or di.get(UserController)
    user = await ctrl.get_user("1")
    assert user.name == "John"
    assert user.id == "1"
    assert ctrl.api_key == "some-random-apikey"

    create_user = CreateUser() # or di.get(CreateUser)
    user = await create_user.run(CreateUserRequest(id="1", name="John"))
    assert user.name == "John"

    create_user_fn = create_user_usecase() # or di.get(create_user_usecase)
    user = await create_user_fn(CreateUserRequest(id="1", name="John"))
    assert user.name == "John"

    ```
"""

from .injection import add, bind, bind_all, get, inject
from .registry import (
    AnyBinding,
    AnyProvider,
    Binding,
    Provider,
    ProviderRegistry,
    TValue,
)

__all__ = [
    "add",
    "bind",
    "bind_all",
    "get",
    "inject",
    "AnyBinding",
    "AnyProvider",
    "Binding",
    "Provider",
    "ProviderRegistry",
    "TValue",
]
