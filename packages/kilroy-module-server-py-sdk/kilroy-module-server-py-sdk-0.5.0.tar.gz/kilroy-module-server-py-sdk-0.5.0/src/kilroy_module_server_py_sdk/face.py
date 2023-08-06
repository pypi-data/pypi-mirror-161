from abc import ABC, abstractmethod
from typing import AsyncIterable, Generic, Set, Tuple
from uuid import UUID

from kilroy_module_py_shared import JSON, JSONSchema

from kilroy_module_server_py_sdk.metrics import Metric
from kilroy_module_server_py_sdk.types import StateType
from kilroy_module_server_py_sdk.utils import ConfigurableWithLoadableState


class Face(ConfigurableWithLoadableState[StateType], Generic[StateType], ABC):
    @property
    @abstractmethod
    def post_schema(self) -> JSONSchema:
        pass

    @property
    @abstractmethod
    def metrics(self) -> Set[Metric]:
        pass

    @abstractmethod
    def generate(self, n: int) -> AsyncIterable[Tuple[UUID, JSON]]:
        pass

    @abstractmethod
    async def fit_post(self, post: JSON) -> None:
        pass

    @abstractmethod
    async def fit_score(self, post_id: UUID, score: float) -> None:
        pass

    @abstractmethod
    async def step(self) -> None:
        pass
