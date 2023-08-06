"""Declares :class:`NullSession`."""
from typing import Any

import fastapi

from .basesession import BaseSession


class NullSession(BaseSession):
    """A session implementation that does nothing."""
    __module__: str = 'cbra.session'

    async def add_to_response(self, response: fastapi.Response) -> None:
        pass

    async def get(self, key: str) -> Any:
        return None

    async def set(self, key: str, value: Any) -> None:
        pass