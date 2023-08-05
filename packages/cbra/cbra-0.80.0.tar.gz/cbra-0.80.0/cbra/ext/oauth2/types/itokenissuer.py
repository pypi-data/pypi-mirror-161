"""Declares :class:`ITokenIssuer`."""
from ckms.jose import PayloadCodec
from ckms.types import JSONWebToken

from .iclient import IClient
from .isubjectrepository import ISubjectRepository
from .servermetadata import ServerMetadata


class ITokenIssuer:
    __module__: str = 'cbra.ext.oauth2.types'

    #: Specifies the maximum age of an assertion.
    max_assertion_age: int = 30000

    #: Specifies the time-to-live of an access token if not otherwise
    #: specified, in seconds.
    default_ttl: int = 300

    #: The client that is handling the token request.
    client: IClient

    #: The concrete :class:`~cbra.ext.oauth2.ISubjectRepository`
    #: implementation that is used to lookup :term:`Subjects`.
    subjects: ISubjectRepository

    #: A :class:`~ckms.ext.oauth2.ServerMetadata` instance describing
    #: the authorization server that is issueing a token.
    metadata: ServerMetadata

    #: A :class:`ckms.jose.PayloadCodec` instance that knows how to
    #: decrypt JWE objects that were encrypted using the keys exposed
    #: at the JWKS URL.
    codec: PayloadCodec

    #: Indicates if a lookup of the JWKS of any issuer is allowed.
    allow_jwks_lookups: bool = True

    #: The set of trusted issuers for which the keys may be retrieved.
    trusted_issuers: set[str] = set()

    #: The URL of the local issuer i.e. the server. It is assumed that
    #: all tokens issued by this server have this value set to their
    #: issuer attribute.
    issuer: str

    def is_local_issued(self, claims: JSONWebToken) -> bool:
        raise NotImplementedError