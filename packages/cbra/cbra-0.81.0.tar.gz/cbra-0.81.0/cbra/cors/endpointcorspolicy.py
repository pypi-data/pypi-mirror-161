"""Declares :class:`EndpointCorsPolicy`."""
from typing import NoReturn

import fastapi

from cbra.utils import docstring
from cbra.types import IRequestHandler
from .basecorspolicy import BaseCorsPolicy


class EndpointCorsPolicy(BaseCorsPolicy):
    """A :class:`BaseCorsPolicy` implementation that defers the
    enforcement of the policy to the endpoint. This policy may
    be used when the endpoint has additional knowledge that is
    needed to determine if a cross-origin request is allowed to
    be served.

    The policy always accepts preflight requests that match the
    configured parameters.
    """
    __module__: str = 'cbra.cors'

    @docstring(BaseCorsPolicy)
    async def process_request(
        self,
        request: fastapi.Request,
        handler: IRequestHandler,
        origin: str | None = None
    ) -> bool | NoReturn:
        return await super().process_request(request, handler, origin)

    @docstring(BaseCorsPolicy)
    async def process_response(
        self,
        request: fastapi.Request,
        response: fastapi.Response,
        handler: IRequestHandler,
        origin: str | None = None
    ) -> None | NoReturn:
        if origin is None or origin == self.server:
            return

        if str.upper(request.method) == "OPTIONS":
            return await self.process_options_response(
                request=request,
                response=response,
                handler=handler
            )

        # It is assumed here that the endpoint rejected the request if
        # the CORS policy did not accept the origin or other parameters.
        # This basically means that CORS headers should be added allowing
        # all properties of the given response object.
        headers = {
            'Access-Control-Allow-Origin': self.origin,
            'Access-Control-Allow-Credentials': str(self.allow_credentials).lower()
        }
        response.headers.update(headers) # type: ignore

    async def process_options_response(
        self,
        request: fastapi.Request,
        response: fastapi.Response,
        handler: IRequestHandler,
        origin: str | None = None
    ) -> None | NoReturn:
        headers = {}
        headers['Access-Control-Allow-Credentials'] =\
            str(self.allow_credentials).lower()
        headers['Access-Control-Allow-Methods'] =\
            str.join(',', sorted(self.allowed_methods))
        headers['Access-Control-Allow-Origin'] = self.origin
        if self.allowed_headers:
            headers['Access-Control-Allow-Headers'] = str.join(
                ', ',
                sorted(self.allowed_headers)
            )
        response.headers.update(headers) # type: ignore