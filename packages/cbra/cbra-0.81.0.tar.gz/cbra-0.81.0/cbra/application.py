"""Declares :class:`Application`."""
import asyncio
import logging
import typing

import aorta
import fastapi
import unimatrix.runtime
from ckms.core import get_default_keychain
from ckms.core import Keychain
from ckms.jose import PayloadCodec
from ckms.types import JSONWebKeySet
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from h11 import RemoteProtocolError
from starlette.middleware.base import BaseHTTPMiddleware
from unimatrix.exceptions import CanonicalException

from .apiroute import APIRoute
from .exceptions import BaseRedirectingException
from .exceptions import TryAgain
from .exceptions import UnprocessableEntity
from .exceptions import UpstreamServiceNotAvailable
from .exceptions import UpstreamConnectionFailure
from .ext import ioc
from .types import IRequestHandler
from .types import IRouteable


class Application(fastapi.FastAPI):
    logger: logging.Logger = logging.getLogger('uvicorn')

    #: The JWT codec used by the server for signing and encryption.
    codec: PayloadCodec

    #: The JSON Web Key Set (JWKS) offered by the server to encrypt
    #: data and verify signatures.
    jwks: JSONWebKeySet

    #: Tags to include in the JWKS.
    jwks_tags: list[str]

    #: The keychain holding the decryption and signing keys
    #: used by the server.
    keychain: Keychain

    #: A :class:`aorta.MessagePublisher` implementation that is used
    #: to publish messages.
    publisher: aorta.MessagePublisher

    def __init__(
        self,
        provider: ioc.Provider | None = None,
        log_exceptions: bool = False,
        jwks: JSONWebKeySet | None = None,
        jwks_tags: list[str] | None = None,
        keychain: Keychain | None = None,
        publisher: aorta.MessagePublisher | None = None,
        *args: typing.Any,
        **kwargs: typing.Any
    ):
        """The :class:`cbra.Application` class integrates :mod:`cbra` with
        the underlying ASGI implementations (:mod:`fastapi` and :mod:`starlette`).

        The `provider` argument specifies the container to use when injecting
        dependencies. If `provider` is ``None`` (the default) then a new
        container is instantiated. In that case, the
        :attr:`cbra.conf.settings.DEPENDENCIES` is also evualated to inject
        dependencies based on the runtime settings. It is assumed that, if the
        dependency injection container is explicitely provided to the
        constructor, it does not need any further configuration.

        With `log_exceptions`, the application may be configured to explicitely
        log :exc:`cbra.exceptions.CanonicalException` instances. The default
        is ``False``.
        """
        self.jwks = jwks or JSONWebKeySet()
        self.jwks_tags = jwks_tags or ['server']
        self.keychain = keychain if keychain is not None else get_default_keychain()
        self.codec = PayloadCodec(
            decrypter=self.keychain,
            encrypter=self.keychain,
            signer=self.keychain,
            verifier=self.keychain
        )
        self.publisher = publisher or aorta.MessagePublisher(
            transport=aorta.transport.NullTransport()
        )
        on_startup = kwargs.setdefault('on_startup', [])
        on_startup.append(self.on_startup)
        on_shutdown = kwargs.setdefault('on_shutdown', [])
        on_shutdown.append(self._teardown)
        self.container = provider
        if self.container is None:
            self.container = ioc

        self.log_exceptions = log_exceptions
        kwargs.setdefault('docs_url', '/ui')
        kwargs.setdefault('openapi_tags', [])
        kwargs.setdefault('redoc_url', '/docs')
        exception_handlers = kwargs.setdefault('exception_handlers', {})
        exception_handlers.update({
            asyncio.TimeoutError: self.canonical_exception,
            BaseRedirectingException: self.canonical_exception,
            CanonicalException: self.canonical_exception,
            ConnectionError: self.canonical_exception,
            RequestValidationError: self.canonical_exception,
            TimeoutError: self.canonical_exception,
            RemoteProtocolError: self.canonical_exception,
        })
        super().__init__(*args, **kwargs)
        self.router.route_class = APIRoute
        self.add_middleware(BaseHTTPMiddleware, dispatch=self.handle_session)
        self.add_api_route(
            path='/.well-known/host-meta.json',
            endpoint=self.metadata
        )

    async def handle_session(
        self,
        request: fastapi.Request,
        call_next: typing.Callable[..., typing.Coroutine[None, None, fastapi.Response]]
    ) -> fastapi.Response:
        response = await call_next(request)
        if request.scope.get('session'):
            await request.scope['session'].add_to_response(response)
        return response

    def add(self,
        handler: typing.Union[
            IRouteable,
            type[IRequestHandler],
            type[IRouteable],
        ],
        *args: typing.Any,
        **kwargs: typing.Any
    ):
        """Add a request handler to the :class:`Application`."""
        handler.add_to_router(app=self, *args, **kwargs)

    def add_api_route(self, *args: typing.Any, **kwargs: typing.Any): # type: ignore
        return super().add_api_route(*args, **kwargs)

    async def add_key(
        self,
        *,
        name: str,
        params: typing.Any
    ) -> None:
        """Add a key to the application and ensure that the key metadata
        is loaded.
        """
        self.keychain.configure({name: params})
        await self.keychain

    async def add_encryption_key(self, name: str, params: typing.Any) -> None:
        """Add a encryption key to the application and ensure that the key metadata
        is loaded.
        """
        params.update({
            'use': 'enc'
        })
        return await self.add_key(name=name, params=params)

    async def add_signing_key(self, name: str, params: typing.Any) -> None:
        """Add a signing key to the application and ensure that the key metadata
        is loaded.
        """
        params.update({
            'use': 'sig'
        })
        return await self.add_key(name=name, params=params)

    async def on_startup(self):
        await self._boot()

    async def _boot(self): # pragma: no cover
        self.logger.info("Booting up ASGI application")
        await unimatrix.runtime.on('boot')
        await self.keychain
        if self.jwks_tags:
            keychain = self.keychain.tagged(self.jwks_tags)
            self.jwks = keychain.as_jwks(private=False)
        await self.boot()

    async def boot(self): # pragma: no cover
        """Invoked when the :class:`Application` is starting up. Subclasses
        may override this method to customize the behavior of the
        :class:`Application` during boot.

        Common use cases to override :meth:`boot()` is to establish database
        connections, fetch the public keys of consumed systems, or other
        run configurations that depend on active connections to other services.
        """
        pass

    async def canonical_exception(
        self,
        request: fastapi.Request,
        exception: BaseException
    ) -> typing.NoReturn | fastapi.Response:
        """Handles a canonical exception to a standard error message format."""
        origin = request.headers.get('Origin')
        if isinstance(exception, BaseRedirectingException):
            response = exception.as_response()
            if not response.headers.get('Access-Control-Allow-Origin') and origin:
                response.headers['Access-Control-Allow-Origin'] = origin
            return response
        if isinstance(exception, ConnectionRefusedError):
            kwargs = {}
            return await self.canonical_exception(
                request,
                UpstreamServiceNotAvailable(**kwargs),
            )
        elif isinstance(
            exception,
            (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)
        ):
            kwargs = {}
            return await self.canonical_exception(
                request,
                UpstreamConnectionFailure(**kwargs),
            )
        #elif isinstance(exception, UnsatisfiedDependency):
        #    return await self.canonical_exception(
        #        request, FeatureNotSupported()
        #    )
        elif isinstance(exception, RequestValidationError):
            return await self.canonical_exception(
                request=request,
                exception=UnprocessableEntity.fromexc(exception)
            )
        elif isinstance(exception, (asyncio.TimeoutError, TimeoutError)):
            #count = int(request.headers.get('X-Retry') or 0)
            return await self.canonical_exception(request, TryAgain(30))
        elif isinstance(exception, CanonicalException):
            status_code = getattr(exception, 'http_status_code', None) or 500
            if self.log_exceptions:
                self.logger.error(
                    "%s (%s): %s",
                    exception.code,
                    exception.http_status_code,
                    exception.message
                )
                exception.log(self.logger.exception)
            response = JSONResponse(
                status_code=status_code,
                content=exception.as_dict(),
                headers=exception.http_headers
            )

            # TODO: Ensure that a Javascript client can see the error response.
            # It is assumed here that if the client made a request that was able
            # to trigger an exception, it succesfully passed either a CORS
            # preflight check or it is a safe method, or if the CORS request
            # was not allowed it was rejected by the endpoint.
            if not response.headers.get('Access-Control-Allow-Origin') and origin:
                response.headers['Access-Control-Allow-Origin'] = origin
            return response
        else:
            raise NotImplementedError

    def get_jwks(self) -> JSONWebKeySet:
        return self.jwks

    def metadata(self, request: fastapi.Request):
        return {
            'subject': str(request.url)
        }

    def openapi(self) -> dict[str, typing.Any]:
        if not self.openapi_schema:
            schema = super().openapi()

            # Remove some hardcoded stuff from endpoints where it is
            # not relevant, such as the 422 response for OPTIONS
            # endpoints.
            for path in schema['paths'].values():
                if 'options' in path and '422' in path['options']['responses']:
                    del path['options']['responses']['422']

            self.openapi_schema = schema
        return self.openapi_schema

    async def _teardown(self): # pragma: no cover
        self.logger.info("Tearing down ASGI application")
        await self.teardown()

    async def teardown(self): # pragma: no cover
        """Invoked when the :class:`cbra.Application` is tearing down."""
        pass
