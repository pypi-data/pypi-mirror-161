# pylint: skip-file
import asyncio.coroutines
import inspect
import typing

import fastapi
from ckms.jose import PayloadCodec

from cbra.ext import ioc
from .exceptions import Error
from .types import IClientRepository
from .types import IOpenAuthorizationServer
from .types import IStorage
from .types import ISubjectRepository
from .types import IUpstreamProvider


__all__ = [
    'ClientRepository',
    'CurrentServerMetadata',
    'CurrentUpstreamProvider',
    'DownstreamProvider',
    'LocalIssuer',
    'TransientStorage',
    'Server',
    'ServerCodec',
    'ServerJWKS',
    'SubjectRepository',
    'TokenEndpointURL',
    'UpstreamProvider',
]

def _get_server(request: fastapi.Request) -> IOpenAuthorizationServer:
    return request.scope['oauth2']


def get_codec(request: fastapi.Request) -> PayloadCodec:
    return request.scope['oauth2'].codec


def get_downstream_provider(request: fastapi.Request, provider: str) -> IUpstreamProvider:
    return request.app.providers[provider]


def get_upstream_provider(
    request: fastapi.Request,
    provider: str | None = fastapi.Query(
        default=None,
        title="Provider",
        description=(
            "Specifies the upstream identity provider that establishes "
            "the identity of the resource owner. Additional parameters "
            "may be required to construct the request to the upstream "
            "identity provider."
        )
    )
) -> IUpstreamProvider | None:
    """Return a :class:`~cbra.ext.oauth2.types.IUpstreamProvider` implementation
    that is specified by the request parameter, or ``None`` if the parameter was
    not present.
    """
    if provider is not None and provider not in request.app.providers:
        raise Error(
            error="invalid_request",
            error_description=(
                "The upstream identity provider specified by the `provider` "
                "parameter is not known to the authorization server."
            ),
            mode='client'
        )
    return request.app.providers[provider] if provider else None


def get_local_issuer(request: fastapi.Request) -> str:
    return f'{request.url.scheme}://{request.url.netloc}'


def get_server_jwks(request: fastapi.Request):
    keychain = request.app.keychain.tagged('oauth2')
    raise Exception(keychain.as_jwks(private=False))
    return keychain.as_jwks(private=False)


ClientRepository: IClientRepository = ioc.instance(
    'cbra.ext.oauth2.ClientRepository'
)

Server = fastapi.Depends(_get_server)


async def get_server_metadata(
    request: fastapi.Request,
    server: IOpenAuthorizationServer = Server
) -> typing.Any:
    return await server.get_metadata(request)


def get_token_endpoint(request: fastapi.Request) -> str:
    return request.url_for('oauth2.token')


def CurrentUpstreamProvider(name: str) -> IUpstreamProvider:
    def get_upstream_provider(request: fastapi.Request):
        return request.app.providers[name]
    return fastapi.Depends(get_upstream_provider)


CurrentServerMetadata = fastapi.Depends(get_server_metadata)

LocalIssuer = fastapi.Depends(get_local_issuer)

ServerCodec: PayloadCodec = fastapi.Depends(get_codec)

ServerJWKS = fastapi.Depends(get_server_jwks)

SubjectRepository: ISubjectRepository = ioc.instance(
    'cbra.ext.oauth2.SubjectRepository'
)

TokenEndpointURL: str = fastapi.Depends(get_token_endpoint)

TransientStorage: IStorage = ioc.instance(
    'cbra.ext.oauth2.TransientStorage'
)

DownstreamProvider: IUpstreamProvider = fastapi.Depends(get_downstream_provider)

UpstreamProvider: IUpstreamProvider = fastapi.Depends(get_upstream_provider)


class ServerDependant:
    _is_coroutine = asyncio.coroutines._is_coroutine # type: ignore
    attname: str
    call: typing.Callable[..., typing.Any] | None

    @property
    def __signature__(self) -> inspect.Signature:
        assert self.call is not None # nosec
        return inspect.signature(self.call)

    def __init__(self, attname: str):
        self.attname = attname
        self.call = None

    def add_to_server(self, server: typing.Any) -> None:
        """Adds the dependant to the authorization server."""
        self.call = getattr(server, self.attname)
        signature = inspect.signature(self.call)
        for param in signature.parameters.values():
            if not isinstance(param.default, ServerDependant):
                continue
            param.default.add_to_server(server)