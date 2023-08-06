import json
from typing import AsyncIterable, Type, TypeVar

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
from kilroy_ws_client_py_sdk import Client
from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)


class FaceClient:
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

    async def post(self, request: PostRequest, **kwargs) -> PostReply:
        return await self._request("/post", request, PostReply, **kwargs)

    async def score(self, request: ScoreRequest, **kwargs) -> ScoreReply:
        return await self._request("/score", request, ScoreReply, **kwargs)

    async def scrap(
        self, request: ScrapRequest, **kwargs
    ) -> AsyncIterable[ScrapReply]:
        async for data in self._request_stream_out(
            "/scrap", request, ScrapReply, **kwargs
        ):
            yield data
