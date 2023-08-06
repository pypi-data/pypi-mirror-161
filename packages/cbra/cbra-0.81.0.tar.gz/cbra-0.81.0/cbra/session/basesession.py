"""Declares :class:`BaseSession`."""
from typing import Any
from typing import Awaitable

import fastapi
from ckms.jose import PayloadCodec


class BaseSession:
    awaiting: object = object()
    claims: dict[str, Any] | object = awaiting
    created: bool = False
    codec: PayloadCodec
    dirty: set[str]
    path: str= '/'
    request: fastapi.Request
    reserved_keys: set[str] = {"iat", "mod"}

    @classmethod
    def as_dependency(cls) -> Any:
        return fastapi.Depends(cls)

    @classmethod
    def configure(cls, **attrs: Any) -> Any:
        return type(cls.__name__, (cls,), attrs)

    async def add_to_response(self, response: fastapi.Response) -> None:
        raise NotImplementedError

    def clear(self) -> Awaitable[None] | None:
        raise NotImplementedError

    def get(self, key: str) -> Awaitable[Any] | Any:
        raise NotImplementedError

    def set(self, key: str, value: Any) -> Awaitable[None] | None:
        raise NotImplementedError

    def pop(self, key: str) -> Awaitable[None] | None:
        raise NotImplementedError