"""Declares :class:`PushedAuthorizationRequestEndpoint.`"""
import fastapi

import cbra
from .contentnegotiation import ContentNegotiation
from .exceptions import CrossOriginNotAllowed
from .endpoint import Endpoint
from .exceptions import Error
from .params import ClientRepository
from .params import SubjectRepository
from .params import TransientStorage
from .parsers import JARParser
from .types import AuthorizationRequest
from .types import IClient
from .types import IClientRepository
from .types import IStorage
from .types import ISubject
from .types import ISubjectRepository
from .types import JAR


class PushedAuthorizationRequestEndpoint(Endpoint):
    __module__: str = 'cbra.ext.oauth2'
    allowed_methods: set[str] = {"POST", "OPTIONS"}
    default_ttl: int = 3600
    client: IClient | None
    error_mode: str = 'client'
    storage: IStorage
    methods: set[str] = {"POST"}
    summary: str = "Pushed Authorization Request"
    description: str = (
        "Clients may create prepared authorization requests by pushing "
        "the parameters, as used with a regular authorization request, "
        "to this endpoint. The parameters are serialized as JSON object "
        "and subsequently encoded using one of the content types listed "
        "below.\n\n"
        "Payloads with the following content types are accepted by the "
        "Pushed Authorization Request endpoint:\n\n"
        "- `application/oauth-authz-req+jwt` - a JWT-Secured Authorization "
        "Request (JAR), as specified in RFC 9101. Only confidential clients "
        "are able to invoke the endpoint using this payload type, since the "
        "specification requires the JAR to be signed. After signing a JAR, "
        "it may be encrypted using any of the public keys published at the "
        "`jwks_uri` declared by the authorization servers' metadata.\n"
        "- `application/jwt` - the payload is encrypted using JSON Web "
        "Encryption (JWE) containing a JSON Web Token (JWT). It **must "
        "not** contain a JSON Web Signature (JWS). This payload type is "
        "only accepted for public clients. This a proprietary extension "
        "to the OAuth 2.0 specifications. Sending this payload using a "
        "confidential client results in an `invalid_client` error. The JWT "
        "must be encrypted using any of the encryption public keys published "
        "at the `jwks_uri` declared by the authorization servers' "
        "metadata.\n\n"
        "In addition to the parameters accepted by the **Authorization "
        "Endpoint**, the following parameters are defined for this "
        "endpoint:\n\n"
        "- `encryption_key` - the public key from an asymmetric keypair, "
        "represented in the JSON Web Key (JWK) format, that is used to "
        "encrypt the response from the **Token Endpoint**. The keypair "
        "is considered ephemeral - a new keypair **must** be generated "
        "for each pushed authorization request.\n"
        "- `id_token` - an OpenID Connect ID Token that was signed by "
        "an issuer trusted by the authorization server. The ID Token is "
        "encoded in a JSON Web Signature (JWS). This parameter may be "
        "used if the **Authorization Endpoint** has no means to identify "
        "the resource owner on whose behalf the authorization request is "
        "made. If it *does* know how to identify the resource owner, then "
        "`id_token` **should** be omitted, and in the case that it is not, "
        "the `sub` claim **must** match the subject identifier of the "
        "resource owner identified by the **Authorization Endpoint**.\n"
        "- `access_token` - like `id_token`, but an RFC 9068 access token "
        "signed by a trusted issuer.\n\n"
        "If either the of the above parameters are included in the "
        "authorization request, the request **must** be encrypted."
    )
    negotiation: type[cbra.types.IContentNegotiation] = ContentNegotiation
    renderers: list[type[cbra.types.IRenderer]] = [
        cbra.renderers.JSONRenderer
    ]
    options_description: str = (
        "Communicates the allowed methods and CORS options for "
        "the **Pushed Authorization Request** endpoint."
    )
    parsers: list[type[cbra.types.IParser]] = [
        JARParser
    ]

    def __init__(
        self,
        clients: IClientRepository = ClientRepository,
        storage: IStorage = TransientStorage,
        subjects: ISubjectRepository = SubjectRepository
    ):
        self.client = None
        self.clients = clients
        self.storage = storage
        self.subjects = subjects

    async def enforce_cors_policy( # type: ignore
        self,
        dto: JAR,
        origin: str | None = fastapi.Header(
            default=None,
            alias='Origin'
        )
    ) -> None:
        """Determine if the client allows a cross-origin request from the
        given origin.
        """
        client = await self.get_client(dto)
        if not client.allows_origin(origin):
            raise CrossOriginNotAllowed

    def create_urn(self, dto: AuthorizationRequest) -> str:
        """Create the URN to be used in the ``request_uri`` parameter."""
        assert dto.request_id is not None # nosec
        return f'urn:ietf:params:oauth:request_uri:{dto.request_id}'

    async def get_client(self, par: JAR) -> IClient:
        """Return the client that is requesting access on the behalf
        of the resource owner.
        """
        if self.client is None:
            self.client = await self.clients.get(par.client_id)
        return self.client

    async def get_subject(self, par: JAR) -> ISubject | None:
        """Return the subject that represents the resource owner."""
        return None

    async def handle(self, par: JAR) -> dict[str, int | str]: # type: ignore
        """Handles a **Pushed Authorization Request (PAR)**. The signature,
        client and claims are considered to be validated by the request
        body parser.
        """
        dto = AuthorizationRequest.fromparams(par)
        try:
            await dto.validate_request_parameters(
                client=await self.get_client(par),
                subject=await self.get_subject(par)
            )
        except Error as exception:
            # Set mode to 'client' to explicitely prevent redirects,
            # since this endpoint does not interact with the resource
            # owner.
            exception.mode = 'client'
            raise exception
        await self.storage.persist(dto)
        return {
            'request_uri': self.create_urn(dto),
            'expires_in': self.default_ttl
        }