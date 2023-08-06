from abc import ABC, abstractmethod
from typing import AsyncIterable, Generic

from kilroy_module_py_shared import (
    SeriesMetricInfo,
    SeriesMetricNotificationData,
    TimeseriesMetricInfo,
    TimeseriesMetricNotificationData,
)

from kilroy_module_server_py_sdk.types import (
    MetricInfoType,
    MetricNotificationType,
)
from kilroy_module_server_py_sdk.utils import Observable


class Metric(Generic[MetricInfoType, MetricNotificationType], ABC):
    def __init__(self) -> None:
        super().__init__()
        self._observable = Observable()

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def info(cls) -> MetricInfoType:
        pass

    async def report(self, data: MetricNotificationType) -> None:
        await self._observable.notify(data)

    async def watch(self) -> AsyncIterable[MetricNotificationType]:
        async for data in self._observable.subscribe():
            yield data


class SeriesMetric(
    Metric[SeriesMetricInfo, SeriesMetricNotificationData], ABC
):
    pass


class TimeseriesMetric(
    Metric[TimeseriesMetricInfo, TimeseriesMetricNotificationData], ABC
):
    pass
