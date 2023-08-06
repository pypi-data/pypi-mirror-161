"""Declares :class:`AuthorizationEndpoint`."""
import typing

import fastapi

from cbra.types import IPrincipal
from .authorizationrequestclient import AuthorizationRequestClient
from .endpoint import Endpoint
from .exceptions import CrossOriginNotAllowed
from .exceptions import Error
from .exceptions import LoginRequired
from .params import DownstreamProvider
from .params import LocalIssuer
from .params import Server
from .params import SubjectRepository
from .params import TransientStorage
from .params import UpstreamProvider
from .requestobjectdecoder import RequestObjectDecoder
from .rfc9068principal import RFC9068Principal
from .types import AuthorizationRequest
from .types import AuthorizationRequestParameters
from .types import IAuthorizationServer
from .types import IAuthorizeEndpoint
from .types import IClient
from .types import IStorage
from .types import ISubject
from .types import ISubjectRepository
from .types import IUpstreamProvider
from .types import JAR


class AuthorizationEndpoint(Endpoint, IAuthorizeEndpoint):
    __module__: str = 'cbra.ext.oauth2'
    summary: str = "Authorization Endpoint"
    decoder: RequestObjectDecoder
    description: str = (
        "The **Authorization Endpoint** is used to interact with the resource "
        "owner and obtain an authorization grant."
    )
    login_endpoint: str | None
    login_url: str | None
    methods: set[str] = {"GET"}
    query_model: type[AuthorizationRequestParameters] = AuthorizationRequestParameters
    require_authentication: bool = False
    options_description: str = (
        "Communicates the allowed methods and CORS options for "
        "the **Authorization Request** endpoint."
    )
    principal_factory: typing.Callable[..., IPrincipal] = RFC9068Principal(
        auto_error=False
    )
    provider: IUpstreamProvider | None

    #@classmethod
    #def add_to_router( # type: ignore
    #    cls,
    #    *,
    #    app: fastapi.FastAPI,
    #    base_path: str = '/',
    #    **kwargs: typing.Any
    #) -> None:
    #    """Add the authorization endpoint and the upstream return path to the
    #    ASGI application.
    #    """
    #    base_path = str.rstrip(base_path, '/')
    #    super().add_to_router(
    #        app=app,
    #        base_path=f'{base_path}/authorize',
    #        name='oauth2.authorize',
    #        **kwargs
    #    )
    #    if typing.cast(IAuthorizationServer, app).providers:
    #        app.add_api_route(
    #            endpoint=cls.callback,
    #            path=f'{base_path}/callback/{{provider}}',
    #            name='oauth2.callback',
    #            summary="Upstream Return Endpoint",
    #            description=(
    #                "The return path for upstream identity providers after "
    #                "completing the authentication and/or authorization "
    #                "flow(s)."
    #            ),
    #            methods=['GET', 'POST']
    #        )

    def __init__(
        self,
        decoder: RequestObjectDecoder = fastapi.Depends(),
        issuer: str = LocalIssuer,
        server: IAuthorizationServer = Server,
        storage: IStorage = TransientStorage,
        subjects: ISubjectRepository = SubjectRepository,
        provider: IUpstreamProvider | None = UpstreamProvider
    ):
        self.decoder = decoder
        self.issuer = issuer
        self.login_url = server.login_url
        self.login_endpoint = server.login_endpoint
        self.provider = provider
        self.storage = storage
        self.subjects = subjects

    @staticmethod
    async def callback(
        request: fastapi.Request,
        provider: IUpstreamProvider = DownstreamProvider,
        storage: IStorage = TransientStorage
    ) -> fastapi.Response:
        """Return path for upstream identity providers."""
        return await provider.on_return(storage, request)

    async def create_redirect(
        self,
        dto: AuthorizationRequest
    ) -> str:
        """Return the redirect URI for a previously validated
        :class:`AuthorizationRequest`.
        """
        if self.provider is not None:
            return await self.create_upstream_redirect(dto=dto)

        redirect_uri = None
        assert dto.redirect_uri is not None # nosec
        assert bool(dto.authorization_code) # nosec
        redirect_uri = dto.redirect_uri.authorize(
            code=dto.authorization_code,
            iss=self.issuer,
            state=dto.state
        )
        assert redirect_uri is not None # nosec
        return redirect_uri

    async def create_upstream_redirect(
        self,
        dto: AuthorizationRequestParameters
    ) -> str:
        """Return a string containing the redirection endpoint at the
        upstream identity provider.
        """
        assert self.provider is not None # nosec
        return await self.provider.create_redirect(self.request, dto)

    async def enforce_cors_policy( # type: ignore
        self,
        params: AuthorizationRequestParameters = fastapi.Depends(),
        client: IClient = AuthorizationRequestClient,
        origin: str | None = fastapi.Header(
            default=None,
            alias='Origin'
        )
    ):
        if not client.allows_origin(origin):
            raise CrossOriginNotAllowed(
                redirect_uri=client.get_redirect_url(
                    url=params.redirect_uri,
                    fatal=False
                ),
                state=params.state
            )

    async def get_subject(
        self,
        client: IClient,
        principal: IPrincipal,
        dto: AuthorizationRequest
    ) -> ISubject | None:
        """Return a :class:`~cbra.ext.oauth2.types.ISubject` instance
        representing the currently authenticated principal.
        """
        subject = await dto.get_subject(client.client_id, self.subjects)
        if subject and principal:
            if subject.sub != principal.sub:
                raise Error(
                    error="invalid_request",
                    error_description=(
                        "The authenticated subject does not match the subject "
                        "for which the authorization request was created."
                    ),
                    mode='client'
                )
        elif not subject and principal:
            subject = await self.subjects.get(
                client_id=client.client_id,
                subject_id=principal.sub
            )
        return subject

    async def resolve(
        self,
        client: IClient,
        params: AuthorizationRequestParameters
    ) -> AuthorizationRequest:
        """Inspect the authorization request and determine if it
        needs to be retrieved from the storage or an external source,
        if the `request` or `request_uri` parameters are provided.
        Otherwise return the request.
        """
        if params.request and params.request_uri:
            raise Error(
                error_description=(
                    "An authorization request can not include both the "
                    "\"request\" and \"request_uri\" parameters."
                )
            )
        if params.is_object():
            # A Request Object as specified in RFC 9101
            assert params.request is not None
            claims = await self.decoder.decode_request_object(params.request)
            return AuthorizationRequest.fromparams(JAR(**claims))

        if not params.is_reference():
            return AuthorizationRequest.fromparams(params)
        if params.is_external():
            raise Error(
                error="invalid_request_uri",
                error_description=(
                    "The application does not allow retrieving authorization "
                    "request parameters from the uri that was provided with "
                    "the \"request_uri\" parameter."
                )
            )

        assert params.request_id is not None # nosec
        return await self.storage.get_authorization_request(params.request_id)

    async def handle(
        self,
        client: IClient = AuthorizationRequestClient,
        params: AuthorizationRequestParameters = fastapi.Depends()
    ):
        """Initiates the **Authorization Code Flow**."""
        dto = await self.resolve(client, params)
        try:
            subject = await self.get_subject(
                client=client,
                principal=self.principal,
                dto=dto
            )
        except self.subjects.SubjectDoesNotExist:
            subject = None
        if subject is None:
            self.on_login_required(dto)
        assert subject is not None # nosec

        # Check if the request parameters are valid.
        await self.validate_request(
            client=client,
            subject=subject,
            dto=dto
        )

        # Check if the subject allows the scope requested. If the subject
        # does not allow the scope requested, redirect to the consent_url
        # or present a page when the subject can allow the scope.
        if not subject.allows_scope(dto.scope):
            return self.redirect_consent(dto)

        redirect_uri = await self.create_redirect(dto=dto)
        await self.persist(dto)
        return fastapi.responses.RedirectResponse(
            url=redirect_uri,
            status_code=303
        )

    def on_login_required(self, dto: AuthorizationRequest):
        """Raises an exception indicating that authentication is required."""
        if dto.is_openid() and not dto.can_interact():
            raise Error(
                error="login_required",
                error_description=(
                    "Provide credentials using the designated mechanisms."
                ),
                redirect_uri=dto.redirect_uri,
                mode='redirect'
            )

        if self.login_endpoint:
            raise NotImplementedError

        if self.login_url:
            raise LoginRequired(
                redirect_to=self.login_url,
                params={'next': str(self.request.url)}
            )

    async def persist(
        self,
        dto: AuthorizationRequest
    ) -> None:
        """Inspect the request parameters and persist the appropriate
        objects to the transient storage.
        """
        await self.storage.persist(dto)
        if dto.needs_authorization_code():
            await self.storage.persist(dto.get_authorization_code())

    def redirect_consent(self, dto: AuthorizationRequest) -> fastapi.Response:
        """Create a response that redirects the user-agent to a
        page where the resource owner can grant consent to the
        client.
        """
        if dto.is_openid() and not dto.can_interact():
            raise Error(
                error="consent_required",
                error_description=(
                    "The resource owner has not granted consent to this client "
                    "for the requested scope, and the authorization server "
                    "was instructed not to prompt the resource owner with an "
                    "interface to obtain consent.\n\n"
                    "This indicates a misconfiguration. Contact your system "
                    "administrator or support department for further "
                    "information."
                ),
                redirect_uri=dto.redirect_uri
            )
        raise NotImplementedError
        
    async def validate_request(
        self,
        client: IClient,
        subject: ISubject,
        dto: AuthorizationRequest
    ) -> None:
        """Validates an OAuth 2.0 authorization request."""
        await dto.validate_request_parameters(client, subject)
        dto.sub = typing.cast(str, subject.sub)