import json
from abc import ABC, abstractmethod
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Type,
    TypeVar,
)

from aiostream import stream
from asyncstdlib import enumerate
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
    StatusEnum,
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

from kilroy_module_server_py_sdk.face import Face

M = TypeVar("M", bound=BaseModel)
N = TypeVar("N", bound=BaseModel)


class BaseController(Controller, ABC):
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
    def watch_status(self) -> AsyncIterable[StatusNotification]:
        pass

    @abstractmethod
    async def config(self) -> Config:
        pass

    @abstractmethod
    async def config_schema(self) -> ConfigSchema:
        pass

    @abstractmethod
    def watch_config(self) -> AsyncIterable[ConfigNotification]:
        pass

    @abstractmethod
    async def set_config(
        self, request: Awaitable[ConfigSetRequest]
    ) -> ConfigSetReply:
        pass

    @abstractmethod
    def generate(
        self, request: Awaitable[GenerateRequest]
    ) -> AsyncIterable[GenerateReply]:
        pass

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
    def watch_metrics(self) -> AsyncIterable[MetricsNotification]:
        pass


class ModuleController(BaseController):
    def __init__(self, face: Face) -> None:
        super().__init__()
        self._face = face

    async def post_schema(self) -> PostSchema:
        return PostSchema(post_schema=self._face.post_schema)

    async def status(self) -> Status:
        ready = self._face.loadable.ready
        return Status(status=StatusEnum.ready if ready else StatusEnum.loading)

    async def watch_status(self) -> AsyncIterable[StatusNotification]:
        old = await self.status()
        async for ready in self._face.loadable.watch():
            new = Status(
                status=StatusEnum.ready if ready else StatusEnum.loading
            )
            yield StatusNotification(old=old, new=new)
            old = new

    async def config(self) -> Config:
        return Config(config=await self._face.config.get())

    async def config_schema(self) -> ConfigSchema:
        return ConfigSchema(
            config_schema=await self._face.config.get_full_schema()
        )

    async def watch_config(self) -> AsyncIterable[ConfigNotification]:
        old = await self.config()
        async for config in self._face.config.watch():
            new = Config(config=config)
            yield ConfigNotification(old=old, new=new)
            old = new

    async def set_config(
        self, request: Awaitable[ConfigSetRequest]
    ) -> ConfigSetReply:
        old = await self.config()
        config = await self._face.config.set((await request).set.config)
        new = Config(config=config)
        return ConfigSetReply(old=old, new=new)

    async def generate(
        self, request: Awaitable[GenerateRequest]
    ) -> AsyncIterable[GenerateReply]:
        request = await request
        async for number, (post_id, post) in enumerate(
            self._face.generate(request.number_of_posts)
        ):
            yield GenerateReply(post_number=number, post_id=post_id, post=post)

    async def fit_posts(
        self, requests: AsyncIterable[FitPostsRequest]
    ) -> FitPostsReply:
        async for request in requests:
            await self._face.fit_post(request.post)
        return FitPostsReply(success=True)

    async def fit_scores(
        self, request: Awaitable[FitScoresRequest]
    ) -> FitScoresReply:
        request = await request
        for score in request.scores:
            await self._face.fit_score(score.post_id, score.score)
        return FitScoresReply(success=True)

    async def step(self, request: Awaitable[StepRequest]) -> StepReply:
        await request
        await self._face.step()
        return StepReply(success=True)

    async def metrics_info(self) -> MetricsInfo:
        return MetricsInfo(
            metrics={
                metric.name(): metric.info() for metric in self._face.metrics
            }
        )

    async def watch_metrics(self) -> AsyncIterable[MetricsNotification]:
        combine = stream.merge(
            *(metric.watch() for metric in self._face.metrics)
        )

        async with combine.stream() as streamer:
            async for data in streamer:
                yield data
