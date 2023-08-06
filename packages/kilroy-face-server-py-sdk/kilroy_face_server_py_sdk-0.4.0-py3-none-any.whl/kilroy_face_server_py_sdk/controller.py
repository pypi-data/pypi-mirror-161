import json
from abc import ABC, abstractmethod
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Type,
    TypeVar,
)

from kilroy_face_py_shared import (
    Config,
    ConfigNotification,
    ConfigSchema,
    ConfigSetReply,
    ConfigSetRequest,
    PostReply,
    PostRequest,
    PostSchema,
    ScoreReply,
    ScoreRequest,
    ScrapReply,
    ScrapRequest,
    Status,
    StatusNotification,
)
from kilroy_ws_server_py_sdk import (
    Controller,
    Get,
    JSON,
    Request,
    RequestStreamOut,
    Subscribe,
)
from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)
N = TypeVar("N", bound=BaseModel)


class FaceController(Controller, ABC):
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

    @Request("/post")
    async def _handle_post(self, data: Awaitable[JSON]) -> JSON:
        return await self._handle_request(self.post, data, PostRequest)

    @Request("/score")
    async def _handle_score(self, data: Awaitable[JSON]) -> JSON:
        return await self._handle_request(self.score, data, ScoreRequest)

    @RequestStreamOut("/scrap")
    async def _handle_scrap(
        self, data: Awaitable[JSON]
    ) -> AsyncIterable[JSON]:
        async for payload in self._handle_request_stream_out(
            self.scrap, data, ScrapRequest
        ):
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

    @abstractmethod
    async def post(self, request: Awaitable[PostRequest]) -> PostReply:
        pass

    @abstractmethod
    async def score(self, request: Awaitable[ScoreRequest]) -> ScoreReply:
        pass

    # noinspection PyUnusedLocal
    @abstractmethod
    async def scrap(
        self, request: Awaitable[ScrapRequest]
    ) -> AsyncIterable[ScrapReply]:
        yield
