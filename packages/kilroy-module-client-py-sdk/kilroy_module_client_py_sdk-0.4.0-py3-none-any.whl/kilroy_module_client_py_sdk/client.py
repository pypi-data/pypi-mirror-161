import json
from typing import AsyncIterable, Iterable, Type, TypeVar, Union

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
from kilroy_ws_client_py_sdk import Client, JSON
from kilroy_ws_py_shared import asyncify
from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)


class ModuleClient:
    def __init__(self, url: str, *args, **kwargs) -> None:
        self._client = Client(url, *args, **kwargs)

    async def _get(self, path: str, model: Type[M], **kwargs) -> M:
        payload = await self._client.get(path, **kwargs)
        return model.parse_obj(payload)

    async def _subscribe(
        self, path: str, model: Type[M], **kwargs
    ) -> AsyncIterable[M]:
        async for payload in self._client.subscribe(path, **kwargs):
            yield model.parse_obj(payload)

    async def _request(
        self,
        path: str,
        request: BaseModel,
        reply_model: Type[M],
        **kwargs,
    ) -> M:
        request_payload = json.loads(request.json())
        reply_payload = await self._client.request(
            path,
            data=request_payload,
            **kwargs,
        )
        return reply_model.parse_obj(reply_payload)

    async def _request_stream_out(
        self,
        path: str,
        request: BaseModel,
        reply_model: Type[M],
        **kwargs,
    ) -> AsyncIterable[M]:
        request_payload = json.loads(request.json())
        async for payload in self._client.request_stream_out(
            path,
            data=request_payload,
            **kwargs,
        ):
            yield reply_model.parse_obj(payload)

    async def _request_stream_in(
        self,
        path: str,
        requests: Union[Iterable[BaseModel], AsyncIterable[BaseModel]],
        reply_model: Type[M],
        **kwargs,
    ) -> M:
        async def _payloads(
            requests: Union[Iterable[BaseModel], AsyncIterable[BaseModel]]
        ) -> AsyncIterable[JSON]:
            async for request in asyncify(requests):
                yield json.loads(request.json())

        reply_payload = await self._client.request_stream_in(
            path,
            data=_payloads(requests),
            **kwargs,
        )
        return reply_model.parse_obj(reply_payload)

    async def post_schema(self, **kwargs) -> PostSchema:
        return await self._get("/post/schema", PostSchema, **kwargs)

    async def status(self, **kwargs) -> Status:
        return await self._get("/status", Status, **kwargs)

    async def watch_status(
        self, **kwargs
    ) -> AsyncIterable[StatusNotification]:
        async for data in self._subscribe(
            "/status/watch", StatusNotification, **kwargs
        ):
            yield data

    async def config(self, **kwargs) -> Config:
        return await self._get("/config", Config, **kwargs)

    async def config_schema(self, **kwargs) -> ConfigSchema:
        return await self._get("/config/schema", ConfigSchema, **kwargs)

    async def watch_config(
        self, **kwargs
    ) -> AsyncIterable[ConfigNotification]:
        async for data in self._subscribe(
            "/config/watch", ConfigNotification, **kwargs
        ):
            yield data

    async def set_config(
        self, request: ConfigSetRequest, **kwargs
    ) -> ConfigSetReply:
        return await self._request(
            "/config/set", request, ConfigSetReply, **kwargs
        )

    async def generate(
        self, request: GenerateRequest, **kwargs
    ) -> AsyncIterable[GenerateReply]:
        async for data in self._request_stream_out(
            "/generate", request, GenerateReply, **kwargs
        ):
            yield data

    async def fit_posts(
        self,
        requests: Union[
            Iterable[FitPostsRequest],
            AsyncIterable[FitPostsRequest],
        ],
        **kwargs,
    ) -> FitPostsReply:
        return await self._request_stream_in(
            "/fit/posts", requests, FitPostsReply, **kwargs
        )

    async def fit_scores(
        self, request: FitScoresRequest, **kwargs
    ) -> FitScoresReply:
        return await self._request(
            "/fit/scores", request, FitScoresReply, **kwargs
        )

    async def step(self, request: StepRequest, **kwargs) -> StepReply:
        return await self._request("/step", request, StepReply, **kwargs)

    async def metrics_info(self, **kwargs) -> MetricsInfo:
        return await self._get("/metrics/info", MetricsInfo, **kwargs)

    async def watch_metrics(
        self, **kwargs
    ) -> AsyncIterable[MetricsNotification]:
        async for data in self._subscribe(
            "/metrics/watch", MetricsNotification, **kwargs
        ):
            yield data
