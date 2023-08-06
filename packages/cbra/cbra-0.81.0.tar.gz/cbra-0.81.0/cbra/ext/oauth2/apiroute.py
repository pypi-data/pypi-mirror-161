"""Declares :class:`APIRoute`."""
import typing

import fastapi
import fastapi.routing
import starlette.requests
import starlette.responses
import starlette.types
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint


__all__ = ['APIRoute']


class APIRoute(fastapi.routing.APIRoute):
    app: fastapi.FastAPI
    server: typing.Any
    middleware: list[Middleware]

    @classmethod
    def with_server(
        cls,
        server: fastapi.APIRouter
    ) -> type[fastapi.routing.APIRoute]:
        """Add the OAuth 2.0 router to the :class:`APIRoute` and set
        the appropriate middleware so that other components can detect
        the server.
        """
        return type(cls.__name__, (cls,), {
            'middleware': [
                Middleware(AuthorizationServerMiddleware, server=server)
            ]
        })

    def __init__(self, *args: typing.Any, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        for cls, options in reversed(self.middleware or []): # type: ignore
            self.app = cls(self.app, **options)


class AuthorizationServerMiddleware(BaseHTTPMiddleware):
    server: fastapi.APIRouter

    def __init__(
        self,
        app: starlette.types.ASGIApp,
        server: fastapi.APIRouter
    ) -> None:
        super().__init__(app)
        self.server = server

    async def dispatch(
        self,
        request: starlette.requests.Request,
        call_next: RequestResponseEndpoint
    ) -> starlette.responses.Response:
        """Add the :class:`~cbra.ext.oauth2.AuthorizationServer` to the
        request object.
        """
        request.scope['oauth2'] = self.server
        return await call_next(request)