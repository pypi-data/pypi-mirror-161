"""Declares :class:`BaseSession`."""
from typing import Any

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

    async def get(self, key: str) -> Any:
        raise NotImplementedError

    async def set(self, key: str, value: Any) -> None:
        raise NotImplementedError
