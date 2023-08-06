"""Declares :class:`BaseCorsPolicy`."""
from typing import Any
from typing import NoReturn

import fastapi

from ..types import ICorsPolicy
from ..types import IRequestHandler


class BaseCorsPolicy(ICorsPolicy):
    """The base class for all Cross-Origin Resource Sharing (CORS)
    policy implementations.
    """
    __module__: str = 'cbra.cors'

    @classmethod
    def new(cls, **attrs: Any) -> type['BaseCorsPolicy']:
        return type(cls.__name__, (cls,), attrs)

    async def get_allowed_origins(self) -> set[str]:
        return self.allowed_origins

    async def process_request(
        self,
        request: fastapi.Request,
        handler: IRequestHandler,
        origin: str | None = None
    ) -> bool | NoReturn:
        """Determine if the origin is allowed to make cross-origin
        requests. Raise an exception if CORS is rejected for the
        given `origin`. If `origin` is ``None``, then it is assumed
        that the request is not cross-origin.
        """
        return True

    async def process_response(
        self,
        request: fastapi.Request,
        response: fastapi.Response,
        handler: IRequestHandler,
        origin: str | None = None
    ) -> None | NoReturn:
        """Sets the appropriate headers on a HTTP response. If `origin`
        is not ``None``, then the origin was allowed to make cross-origin
        requests by this policy instance.
        """
        allow = await self.get_allowed_origins()
        if self.origin not in allow\
        or self.origin is None\
        or self.origin == self.server:
            return
        is_options = request.method == "OPTIONS"
        headers = {}

        # It is assumed here that this method is never executed if the
        # CORS request was rejected by process_request().
        headers['Access-Control-Allow-Origin'] = self.origin
        headers['Access-Control-Allow-Credentials'] = str(self.allow_credentials).lower()
        if self.allowed_response_headers and not is_options:
            headers['Access-Control-Expose-Headers'] = str.join(
                ', ',
                sorted(self.allowed_response_headers)
            )
        if self.allowed_methods:
            headers['Access-Control-Allow-Methods'] = str.join(
                ', ',
                sorted(self.allowed_methods)
            )
        if is_options:
            headers['Access-Control-Max-Age'] = str(self.max_age)
            if self.allowed_headers:
                headers['Access-Control-Allow-Headers'] = str.join(
                    ', ',
                    sorted(self.allowed_headers)
                )
        response.headers.update(headers) # type: ignore