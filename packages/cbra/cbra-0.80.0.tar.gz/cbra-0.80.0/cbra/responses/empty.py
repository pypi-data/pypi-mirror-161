"""Declares :class:`EmptyResponse`."""
from typing import Any

from starlette.responses import Response


class EmptyResponse(Response):
    __module__: str = 'cbra.responses'

    def __init__(self, **kwargs: Any):
        kwargs['status_code'] = 204
        super().__init__(**kwargs)