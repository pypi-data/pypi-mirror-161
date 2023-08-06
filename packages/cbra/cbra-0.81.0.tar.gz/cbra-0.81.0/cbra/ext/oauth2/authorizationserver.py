"""Declares :class:`AuthorizationServer`."""
import enum
import pathlib
import types
import typing

import ckms
import ckms.jose
import fastapi
from ckms.core import Keychain
from ckms.types import IKeychain
from ckms.types import JSONWebKeySet
from fastapi.exceptions import RequestValidationError
from unimatrix.exceptions import CanonicalException

import cbra
from cbra.auth import NullPrincipal
from cbra.ext import ioc
from cbra.types import IEndpoint
from cbra.types import IRouteable
from .apiroute import APIRoute
from .authorizeendpoint import AuthorizationEndpoint
from .exceptions import Error
from .jwksendpoint import JWKSEndpoint
from .memorystorage import MemoryStorage
from .metadataendpoint import MetadataEndpoint
from .nullclientrepository import NullClientRepository
from .nullsubjectrepository import NullSubjectRepository
from .pushedauthorizationrequestendpoint import PushedAuthorizationRequestEndpoint
from .types import IAuthorizeEndpoint
from .types import IStorage
from .types import IClientRepository
from .types import IOpenAuthorizationServer
from .types import IPrincipal
from .types import ISubjectRepository
from .types import ITokenIssuer
from .types import IUpstreamProvider
from .types import IUpstreamReturnHandler
from .types import ServerMetadata
from .tokenissuer import TokenIssuer
from .tokenrequesthandler import TokenRequestHandler


DEFAULT_TAGS: list[enum.Enum | str] = ['OAuth 2.1/OpenID Connect 1.0']
SUMMARY = pathlib.Path(__file__).parent.joinpath('authorizationserver.md')


class AuthorizationServer(fastapi.APIRouter, IOpenAuthorizationServer):
    __module__: str = 'cbra.ext.oauth2'
    _jwks: JSONWebKeySet | None = None
    allowed_signing_algorithms: list[str]
    allowed_content_encryption: list[str]
    asgi: cbra.Application
    authorize: type[IAuthorizeEndpoint]
    authorize_endpoint_name: str = 'oauth2.authorize'
    callbacks: dict[str, type[IUpstreamReturnHandler]] = {}
    clients: type[IClientRepository]
    decryption_alg: str
    decryption_key: str
    enable_authorization: bool
    enable_par: bool
    issuer: type[ITokenIssuer]
    jwks_endpoint_name: str
    jwks_tags: list[str] = ['oauth2']
    login_endpoint: str | None
    login_url: str | None
    metadata: ServerMetadata = ServerMetadata(
        token_endpoint_auth_methods_supported=['private_key_jwt']
    )
    metadata_endpoint_name: str = 'oauth2.metadata'
    metadata_overrides: dict[str, bool | str | list[str]]
    par: type[PushedAuthorizationRequestEndpoint] = PushedAuthorizationRequestEndpoint
    principal_factory: typing.Callable[..., IPrincipal] | type[object]
    providers: dict[str, IUpstreamProvider] = {}
    require_par: bool
    server_name: str | None = None
    signing_alg: str
    signing_key: str
    storage: type[IStorage]
    summary: str = open(SUMMARY).read()
    subjects: type[ISubjectRepository]
    token: type[TokenRequestHandler]

    @property
    def codec(self) -> ckms.jose.PayloadCodec:
        """The :class:`ckms.jose.PayloadCodec` instance that is used by
        the authorization server to sign JWS objects and decrypt JWE
        objects.
        """
        return ckms.jose.PayloadCodec(
            decrypter=self.keychain,
            signer=self.keychain
        )

    @property
    def jwks(self) -> JSONWebKeySet:
        """The JSON Web Key Set (JWKS) containing the public keys used
        by the authorization server."""
        if self._jwks is None:
            self._jwks = self.keychain.tagged(self.jwks_tags).as_jwks(private=False)
        return self._jwks

    @property
    def keychain(self) -> IKeychain:
        """The keychain used by the authorization server to
        sign and decrypt.
        """
        return self.asgi.keychain

    def add_to_router( # type: ignore
        self,
        *,
        app: IRouteable.RouterType,
        base_path: str,
        **kwargs: str
    ) -> None:
        # Configure the OAuth 2.0 server metadata and OpenID Connect
        # Discovery endpoints.
        app = typing.cast(cbra.Application, app)
        if self.server_name is not None:
            raise NotImplementedError
        self.metadata_endpoint.add_to_router(
            app=app,
            base_path='/.well-known/oauth-authorization-server',
            cors_policy=cbra.cors.AnonymousReadCorsPolicy,
            name='oauth2.metadata',
            tags=DEFAULT_TAGS,
            response_model_exclude_defaults=True
        )
        if self.authorize is not None and self.enable_authorization:
            self.authorize.add_to_router( # type: ignore
                app=self,
                base_path='/authorize',
                name='oauth2.authorize'
            )
            self.par.add_to_router(
                app=self,
                base_path='/par',
                name='oauth2.par'
            )

        # Add the JWKS endpoint for this specific API route.
        JWKSEndpoint.add_to_router(
            app=self,
            base_path='/jwks.json',
            name='oauth2.jwks',
            response_model_exclude_defaults=True
        )

        if self.token is not None:
            self.token.add_to_router(
                app=self,
                base_path='/token'
            )

        for cb in self.callbacks.values():
            cb.add_to_router(
                app=self,
                base_path='/callback'
            )

        self.asgi = app
        app.include_router(
            router=self,
            prefix=base_path,
            tags=DEFAULT_TAGS
        )
        app.add_exception_handler(Error, self.on_oauth2_exception) # type: ignore
        app.add_event_handler('startup', self.setup_authorization_server) # type: ignore

        assert app.openapi_tags is not None # nosec
        app.openapi_tags.append({
            'name': DEFAULT_TAGS[0],
            'description': self.summary
        })

    @classmethod
    def fromsettings(cls, settings: types.ModuleType) -> 'AuthorizationServer':
        """Create a new :class:`AuthorizationServer` from a settings module.

        The following members may be defined to configure the server:

        - `OAUTH_SERVER_CONFIG` - A dictionary holding configuration parameters
          for the authorization server e.g.:

          .. code:: python

            OAUTH_SERVER_CONFIG = {
                'signing_key': 'sig
            }

        - `OAUTH_CLIENTS` - Either a string holding the qualified name of a
          class that implements the :class:`cbra.ext.oauth2.types.IClientRepository`
          interface, or a dictionary specifying at least a `class` attribute
          holding the qualified name of the implementation, and additional
          members specifying configuration parameters.
        - `OAUTH_CLIENT_MODEL` - A string holding the qualified name to a Python
          class that is used as the :class:`cbra.ext.oauth2.types.IClient`
          implementation returned from the clients repository.
        """
        raise NotImplementedError

    def __init__(
        self,
        *,
        signing_key: str,
        allowed_content_encryption: list[str] | None = None,
        allowed_signing_algorithms: list[str] | None = None,
        authorize: type[IAuthorizeEndpoint | IEndpoint] = AuthorizationEndpoint,
        callbacks: list[type[IUpstreamReturnHandler]] | None = None,
        clients: type[IClientRepository] | None = None,
        grant_types: set[str] | None = None,
        jwks_tags: list[str] = ['oauth2'],
        jwks_endpoint_name: str = 'metadata.jwks',
        login_endpoint: str | None = None,
        login_url: str | None = None,
        metadata_overrides: dict[str, bool | str | list[str]] | None = None,
        storage: type[IStorage] | None = None,
        subjects: type[ISubjectRepository] = NullSubjectRepository,
        principal_factory: typing.Callable[..., IPrincipal] | type[object] = NullPrincipal,
        providers: list[IUpstreamProvider] | None = None,
        server_name: str | None = None,
        issuer: type[ITokenIssuer] = TokenIssuer,
        token: type[TokenRequestHandler] = TokenRequestHandler,
        par: type[PushedAuthorizationRequestEndpoint] = PushedAuthorizationRequestEndpoint,
        enable_authorization: bool = True,
        enable_par: bool = True,
        require_par: bool = False,
        **kwargs: typing.Any
    ):
        kwargs.setdefault('route_class', APIRoute.with_server(self))
        super().__init__(**kwargs)

        # If the authorization_code grant is not allowed, then there is no point
        # in enabling the authorization endpoints.
        if "authorization_code" not in (grant_types or []):
            enable_authorization = False

        self.allowed_content_encryption = allowed_content_encryption or ['A256GCM']
        self.allowed_signing_algorithms = allowed_signing_algorithms or ['EdDSA', 'PS256']
        self.authorize = typing.cast(
            type[IAuthorizeEndpoint],
            authorize.new(principal_factory=principal_factory) # type: ignore
        )
        self.callbacks = {cb.provider: cb for cb in (callbacks or [])}
        self.clients = clients or NullClientRepository
        self.enable_authorization = enable_authorization
        self.enable_par = enable_authorization and (enable_par or require_par)
        self.issuer = issuer
        self.jwks_endpoint_name = jwks_endpoint_name
        self.jwks_tags = jwks_tags
        self.login_endpoint = login_endpoint
        self.login_url = login_url
        self.metadata_endpoint = MetadataEndpoint.new(server=self)
        self.metadata_endpoint_name = 'oauth2.metadata'
        self.metadata_overrides = metadata_overrides or {}
        self.par = par
        self.providers = {
            provider.name: provider 
            for provider in (providers or [])
        }
        self.require_par = self.enable_par and require_par
        self.server_name = server_name
        self.signing_key = signing_key
        self.storage = storage or MemoryStorage
        self.subjects = subjects
        self.token = token

        ioc.provide('cbra.ext.oauth2.ClientRepository', self.clients, True)
        ioc.provide('cbra.ext.oauth2.SubjectRepository', self.subjects, True)
        ioc.provide('cbra.ext.oauth2.TransientStorage', self.storage, True)
        self.metadata.grant_types_supported = list(sorted(grant_types or []))

    def allows_grant(self, grant_type: str) -> bool:
        """Return a boolean indicating if the server is configured to allow
        the given grant type.
        """
        return grant_type in (self.metadata.grant_types_supported or [])

    def get_jwks(self) -> JSONWebKeySet:
        """Return the :class:`ckms.jose.models.JSONWebKeySet` that is used
        by the server.
        """
        assert self.jwks is not None # nosec
        return self.jwks

    def reverse(self, request: fastapi.Request, name: str) -> str:
        return request.url_for(name)

    async def get_metadata(
        self,
        request: fastapi.Request
    ) -> ServerMetadata:
        assert self.jwks is not None # nosec
        metadata = {
            **self.metadata.dict(),
            'issuer': f'{request.url.scheme}://{request.url.netloc}',
            'token_endpoint': request.url_for('oauth2.token') if self.token else None,
            'jwks_uri': self.reverse(request, 'oauth2.jwks'),
            'require_pushed_authorization_requests': self.require_par
        }
        if self.enable_authorization:
            metadata['authorization_endpoint'] = request.url_for('oauth2.authorize')
        if self.enable_par:
            metadata['request_parameter_supported'] = True
            metadata['request_uri_parameter_supported'] = True
            metadata['request_object_encryption_alg_values_supported'] = self.jwks.get_encryption_algorithms()
            metadata['request_object_encryption_enc_values_supported'] = self.allowed_content_encryption
            metadata['request_object_signing_alg_values_supported'] = self.allowed_signing_algorithms
            metadata['require_request_uri_registration'] = True
            metadata['pushed_authorization_request_endpoint'] = request.url_for('oauth2.par')
        if self.token:
            metadata['token_endpoint_auth_signing_alg_values_supported'] = self.allowed_signing_algorithms
        metadata.update(self.metadata_overrides)
        return ServerMetadata(**metadata)

    async def add_encryption_key(self, name: str, params: dict[str, typing.Any]) -> None:
        """Add an encryption key that is specifically used by the authorization
        server.
        """
        tags = params.setdefault('tags', [])
        for tag in self.jwks_tags:
            if tag in tags:
                continue
            tags.append(tag)
        return await self.asgi.add_encryption_key(name, params)

    async def add_signing_key(self, name: str, params: dict[str, typing.Any]) -> None:
        """Add a signing key that is specifically used by the authorization
        server.
        """
        tags = params.setdefault('tags', [])
        for tag in self.jwks_tags:
            if tag in tags:
                continue
            tags.append(tag)
        return await self.asgi.add_signing_key(name, params)

    async def metadata_redirect(self, request: fastapi.Request):
        return fastapi.responses.RedirectResponse(
            self.reverse(request, self.metadata_endpoint_name),
            status_code=303
        )

    async def setup_authorization_server(self):
        await self.keychain

    async def on_exception(
        self,
        request: fastapi.Request,
        exception: CanonicalException | RequestValidationError
    ) -> fastapi.Response:
        raise exception

    async def on_oauth2_exception(
        self,
        request: fastapi.Request,
        exception: Error
    ) -> fastapi.Response:
        return await exception.as_response(request)