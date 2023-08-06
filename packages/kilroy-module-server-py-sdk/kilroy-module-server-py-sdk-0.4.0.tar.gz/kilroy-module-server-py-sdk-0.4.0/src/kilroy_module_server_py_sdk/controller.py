import json
from abc import ABC, abstractmethod
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Type,
    TypeVar,
)

from kilroy_module_py_shared import (
    Config,
    ConfigNotification,
    ConfigSchema,
    ConfigSetReply,
    ConfigSetRequest,
    FitPostsReply,
    FitPostsRequest,
    FitScoresReply,
    FitScoresRequest,
    GenerateReply,
    GenerateRequest,
    MetricsInfo,
    MetricsNotification,
    PostSchema,
    Status,
    StatusNotification,
    StepReply,
    StepRequest,
)
from kilroy_ws_server_py_sdk import (
    Controller,
    Get,
    JSON,
    Request,
    RequestStreamIn,
    RequestStreamOut,
    Subscribe,
)
from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)
N = TypeVar("N", bound=BaseModel)


class ModuleController(Controller, ABC):
    @staticmethod
    async def _handle_get(fn: Callable[[], Awaitable[M]]) -> JSON:
        payload = await fn()
        return json.loads(payload.json())

    @staticmethod
    async def _handle_subscribe(
        fn: Callable[[], AsyncIterable[M]]
    ) -> AsyncIterable[JSON]:
        async for payload in fn():
            yield json.loads(payload.json())

    @staticmethod
    async def _handle_request(
        fn: Callable[[Awaitable[N]], Awaitable[M]],
        payload: Awaitable[JSON],
        model: Type[N],
    ) -> JSON:
        async def make_request(payload: Awaitable[JSON], model: Type[N]) -> N:
            return model.parse_obj(await payload)

        request = make_request(payload, model)

        try:
            reply = await fn(request)
            return json.loads(reply.json())
        finally:
            request.close()

    @staticmethod
    async def _handle_request_stream_out(
        fn: Callable[[Awaitable[N]], AsyncIterable[M]],
        payload: Awaitable[JSON],
        model: Type[N],
    ) -> AsyncIterable[JSON]:
        async def make_request(payload: Awaitable[JSON], model: Type[N]) -> N:
            return model.parse_obj(await payload)

        request = make_request(payload, model)

        try:
            async for reply in fn(request):
                yield json.loads(reply.json())
        finally:
            request.close()

    @staticmethod
    async def _handle_request_stream_in(
        fn: Callable[[AsyncIterable[N]], Awaitable[M]],
        request_payloads: AsyncIterable[JSON],
        request_model: Type[N],
    ) -> JSON:
        async def make_requests(
            payloads: AsyncIterable[JSON],
        ) -> AsyncIterable[N]:
            async for payload in payloads:
                yield request_model.parse_obj(payload)

        reply = await fn(make_requests(request_payloads))
        return json.loads(reply.json())

    @Get("/post/schema")
    async def _handle_post_schema(self) -> JSON:
        return await self._handle_get(self.post_schema)

    @Get("/status")
    async def _handle_status(self) -> JSON:
        return await self._handle_get(self.status)

    @Subscribe("/status/watch")
    async def _handle_watch_status(self) -> AsyncIterable[JSON]:
        async for payload in self._handle_subscribe(self.watch_status):
            yield payload

    @Get("/config")
    async def _handle_config(self) -> JSON:
        return await self._handle_get(self.config)

    @Get("/config/schema")
    async def _handle_config_schema(self) -> JSON:
        return await self._handle_get(self.config_schema)

    @Subscribe("/config/watch")
    async def _handle_watch_config(self) -> AsyncIterable[JSON]:
        async for payload in self._handle_subscribe(self.watch_config):
            yield payload

    @Request("/config/set")
    async def _handle_set_config(self, data: Awaitable[JSON]) -> JSON:
        return await self._handle_request(
            self.set_config, data, ConfigSetRequest
        )

    @RequestStreamOut("/generate")
    async def _handle_generate(
        self, data: Awaitable[JSON]
    ) -> AsyncIterable[JSON]:
        async for payload in self._handle_request_stream_out(
            self.generate, data, GenerateRequest
        ):
            yield payload

    @RequestStreamIn("/fit/posts")
    async def _handle_fit_posts(self, data: AsyncIterable[JSON]) -> JSON:
        return await self._handle_request_stream_in(
            self.fit_posts, data, FitPostsRequest
        )

    @Request("/fit/scores")
    async def _handle_fit_scores(self, data: Awaitable[JSON]) -> JSON:
        return await self._handle_request(
            self.fit_scores, data, FitScoresRequest
        )

    @Request("/step")
    async def _handle_step(self, data: Awaitable[JSON]) -> JSON:
        return await self._handle_request(self.step, data, StepRequest)

    @Get("/metrics/info")
    async def _handle_metrics_info(self) -> JSON:
        return await self._handle_get(self.metrics_info)

    @Subscribe("/metrics/watch")
    async def _handle_watch_metrics(
        self,
    ) -> AsyncIterable[JSON]:

        async for payload in self._handle_subscribe(self.watch_metrics):
            yield payload

    @abstractmethod
    async def post_schema(self) -> PostSchema:
        pass

    @abstractmethod
    async def status(self) -> Status:
        pass

    @abstractmethod
    async def watch_status(self) -> AsyncIterable[StatusNotification]:
        yield

    @abstractmethod
    async def config(self) -> Config:
        pass

    @abstractmethod
    async def config_schema(self) -> ConfigSchema:
        pass

    @abstractmethod
    async def watch_config(self) -> AsyncIterable[ConfigNotification]:
        yield

    @abstractmethod
    async def set_config(
        self, request: Awaitable[ConfigSetRequest]
    ) -> ConfigSetReply:
        pass

    # noinspection PyUnusedLocal
    @abstractmethod
    async def generate(
        self, request: Awaitable[GenerateRequest]
    ) -> AsyncIterable[GenerateReply]:
        yield

    @abstractmethod
    async def fit_posts(
        self, requests: AsyncIterable[FitPostsRequest]
    ) -> FitPostsReply:
        pass

    @abstractmethod
    async def fit_scores(
        self, request: Awaitable[FitScoresRequest]
    ) -> FitScoresReply:
        pass

    @abstractmethod
    async def step(self, request: Awaitable[StepRequest]) -> StepReply:
        pass

    @abstractmethod
    async def metrics_info(self) -> MetricsInfo:
        pass

    @abstractmethod
    async def watch_metrics(self) -> AsyncIterable[MetricsNotification]:
        yield
