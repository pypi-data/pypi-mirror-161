from abc import ABC, abstractmethod
from asyncio import Queue
from base64 import urlsafe_b64decode, urlsafe_b64encode
from contextlib import asynccontextmanager
from typing import (
    AsyncIterable,
    Dict,
    Generic,
    Iterable,
    List,
    Set,
    Type,
    TypeVar,
)
from uuid import UUID, uuid4

from kilroy_module_py_shared import JSON, JSONSchema

from kilroy_module_server_py_sdk.errors import (
    INVALID_CONFIG_ERROR,
    STATE_NOT_READY_ERROR,
)
from kilroy_module_server_py_sdk.parameters import Parameter
from kilroy_module_server_py_sdk.types import StateType

T = TypeVar("T")


class Observable(Generic[T]):
    _queues: Dict[UUID, Queue[T]]

    def __init__(self) -> None:
        self._queues = {}

    @asynccontextmanager
    async def _create_queue(self) -> Queue[T]:
        queue_id = uuid4()
        queue = Queue()
        self._queues[queue_id] = queue
        yield queue
        self._queues.pop(queue_id)

    async def subscribe(self) -> AsyncIterable[T]:
        async with self._create_queue() as queue:
            while (message := await queue.get()) is not None:
                yield message

    async def notify(self, message: T) -> None:
        for queue in self._queues.values():
            await queue.put(message)


class LoadableState(Generic[StateType]):
    _state: StateType
    _ready: bool
    _observable: Observable[bool]

    def __init__(self) -> None:
        super().__init__()
        self._ready = False
        self._observable = Observable()

    async def _set_ready(self, value: bool) -> None:
        if self._ready != value:
            self._ready = value
            await self._observable.notify(value)

    @staticmethod
    async def _copy_state(state: StateType) -> StateType:
        return await state.__adeepcopy__()

    @staticmethod
    async def _destroy_state(state: StateType) -> None:
        await state.__adestroy__()

    @classmethod
    async def build(cls: Type[T], state: StateType, *args, **kwargs) -> T:
        instance = cls(*args, **kwargs)
        await instance.init(state)
        return instance

    async def init(self, state: StateType) -> None:
        self._state = state
        await self._set_ready(True)

    async def cleanup(self) -> None:
        await self._set_ready(False)
        await self._destroy_state(self._state)

    @asynccontextmanager
    async def load(self) -> StateType:
        await self._set_ready(False)
        try:
            state = await self._copy_state(self._state)
            yield state
            old_state = self._state
            self._state = state
            await self._destroy_state(old_state)
        finally:
            await self._set_ready(True)

    @property
    def state(self) -> StateType:
        if not self._ready:
            raise STATE_NOT_READY_ERROR
        return self._state

    @property
    def ready(self) -> bool:
        return self._ready

    async def watch(self) -> AsyncIterable[bool]:
        async for ready in self._observable.subscribe():
            yield ready


class Configuration(Generic[StateType]):
    _state: LoadableState[StateType]
    _parameters: List[Parameter]
    _observable: Observable[JSON]

    def __init__(
        self, state: LoadableState[StateType], parameters: Iterable[Parameter]
    ) -> None:
        self._state = state
        self._parameters = list(parameters)
        self._observable = Observable()

    async def _get_parameters_mapping(
        self, state: StateType
    ) -> Dict[str, Parameter]:
        return {
            await parameter.name(state): parameter
            for parameter in self._parameters
        }

    async def get(self) -> JSON:
        params = await self._get_parameters_mapping(self._state.state)
        return {
            name: await parameter.get(self._state.state)
            for name, parameter in params.items()
        }

    async def set(self, config: JSON) -> JSON:
        async with self._state.load() as state:
            params = await self._get_parameters_mapping(state)
            for name, value in config.items():
                try:
                    await params[name].set(state, value)
                except Exception as e:
                    raise INVALID_CONFIG_ERROR from e

        config = await self.get()
        await self._observable.notify(config)
        return config

    async def watch(self) -> AsyncIterable[JSON]:
        async for config in self._observable.subscribe():
            yield config

    async def get_full_schema(self) -> JSONSchema:
        return JSONSchema(
            {
                "title": "Module config schema",
                "type": "object",
                "properties": await self.get_properties_schema(),
            }
        )

    async def get_properties_schema(self) -> JSON:
        params = await self._get_parameters_mapping(self._state.state)
        return {
            name: await parameter.schema(self._state.state)
            for name, parameter in params.items()
        }


class ConfigurableWithLoadableState(Generic[StateType], ABC):
    _state: LoadableState[StateType]
    _config: Configuration[StateType]

    @classmethod
    async def build(cls: Type[T], *args, **kwargs) -> T:
        instance = cls(*args, **kwargs)
        state = await instance._create_initial_state()
        params = await instance._get_parameters()
        instance._state = await LoadableState.build(state)
        instance._config = Configuration(instance._state, params)
        return instance

    @abstractmethod
    async def _create_initial_state(self) -> StateType:
        pass

    @abstractmethod
    async def _get_parameters(self) -> Iterable[Parameter]:
        pass

    @property
    def loadable(self) -> LoadableState[StateType]:
        return self._state

    @property
    def state(self) -> StateType:
        return self.loadable.state

    @property
    def config(self) -> Configuration[StateType]:
        return self._config


class Categorizable(ABC):
    @classmethod
    @abstractmethod
    def category(cls) -> str:
        pass

    @classmethod
    def for_category(cls: T, category: str) -> T:
        for subclass in get_all_subclasses(cls):
            if subclass.category() == category:
                return subclass
        raise ValueError(f'Subclass for category "{category}" not found.')

    @classmethod
    def all_categories(cls) -> Set[str]:
        return {subclass.category() for subclass in get_all_subclasses(cls)}


def get_all_subclasses(cls: T) -> Set[T]:
    all_subclasses = set()

    for subclass in cls.__subclasses__():
        all_subclasses.add(subclass)
        all_subclasses.update(get_all_subclasses(subclass))

    return all_subclasses


def base64_encode(value: bytes) -> str:
    return urlsafe_b64encode(value).decode("ascii")


def base64_decode(value: str) -> bytes:
    return urlsafe_b64decode(value.encode("ascii"))
