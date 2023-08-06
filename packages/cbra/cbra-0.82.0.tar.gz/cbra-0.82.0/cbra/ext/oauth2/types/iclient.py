"""Declares :class:`IClient`."""
from typing import cast
from typing import Any
from typing import Union

import ckms
import ckms.jose
import pydantic
from ckms.core.models import JSONWebSignature
from ckms.types import IKeychain
from ckms.types import JSONWebToken

from .granttype import GrantType
from .isubject import ISubject
from .redirecturl import RedirectURL
from .responsetype import ResponseType


class IClient(pydantic.BaseModel):
    """Specifies the interface of OAuth 2.0 client objects.

    An OAuth 2.0 client can be determined from various parameters in an
    HTTP request.

    For requests to the :term:`Authorization Endpoint`, the client is
    specified by the ``client_id`` parameter. This is the case for both
    public clients and confidential clients.

    The client is determined for :term:`Token Endpoint` requests by
    either the ``client_id`` parameter in the request body if the
    client is public, or by the credentials provided in the
    ``Authorization`` header. In the latter case, the ``client_id``
    parameter is absent in the request body.
    """
    __module__: str = 'cbra.ext.oauth2.types'
    __abstract__: bool = True

    client_id: str

    @classmethod
    async def fromquery(
        cls,
        clients: type,
        required: bool = False
    ) -> Any:
        """Return a callable that resolves the current client from the
        query parameters.
        """
        raise NotImplementedError

    @classmethod
    def fromdict(cls, params: dict[str, Any]) -> 'IClient':
        """Construct a new client from a dictionary."""
        raise NotImplementedError

    @classmethod
    def configure(cls, **kwargs: Any) -> 'IClient':
        """Configures the class with the given parameters."""
        return cast(IClient, type(cls.__name__, (cls,), kwargs))

    def as_subject(self) -> ISubject:
        """Return a :class:`~cbra.ext.oauth2.types.ISubject` implementation
        representing the client itself. For use with the client credentials
        grant.
        """
        raise NotImplementedError

    def allows_audience(self, issuer: str, audience: set[str]) -> bool:
        """Return a boolean indicating if the client allows the issueing
        of access token for the given audiences set `audience`.
        """
        raise NotImplementedError

    def allows_scope(self, scope: set[str]) -> bool:
        """Return a boolean indicating if the client allows the given scope."""
        raise NotImplementedError

    def allows_grant_type(self, grant_type: GrantType) -> bool:
        """Return a boolean indicating if the client allows the given grant type."""
        raise NotImplementedError

    def allows_origin(self, origin: str | None) -> bool:
        """Return a boolean indicating if the client allows the given origin in the
        context of Cross-Origin Resource Sharing (CORS).
        """
        raise NotImplementedError

    def allows_response_type(self, response_type: ResponseType) -> bool:
        """Return a boolean indicating if the client allows the given response
        type.
        """
        raise NotImplementedError

    def can_issue_multiple(self) -> bool:
        """Return a boolean indicating if the client allows issueing
        access tokens to multiple audiences.
        """
        raise NotImplementedError

    def get_default_redirect(self) -> str:
        """Return the default redirect URL, if specified."""
        raise NotImplementedError

    def get_consent_url(self, scope: set[str]) -> str:
        """Return the URL at which the resource owner can grant consent
        for the given scope to this client.
        """
        raise NotImplementedError

    def get_redirect_url(
        self,
        url: Union[str, RedirectURL] | None = None,
        fatal: bool = True
    ) -> RedirectURL | None:
        raise NotImplementedError

    def is_confidential(self) -> bool:
        """Return a boolean indicating if the client is confidential and
        must authenticate itself.
        """
        raise NotImplementedError

    def is_public(self) -> bool:
        """Return a boolean indicating if the client is public."""
        raise NotImplementedError

    async def issue_token(
        self,
        *,
        algorithm: str,
        codec: ckms.jose.PayloadCodec,
        issuer: str,
        audience: list[str] | str | set[str] | None,
        subject: ISubject,
        using: str,
        ttl: int,
        scope: set[str]
    ) -> str:
        """Issue an access token encoded as a JSON Web Token (JWT)
        as defined in :rfc:`9068`. Return a string containing the
        token.
        """
        raise NotImplementedError

    async def verify_jws(
        self,
        jws: JSONWebSignature
    ) -> bool:
        """Verify a :class:`~JSONWebSignature` using the public
        keys associated to the client.
        """
        raise NotImplementedError

    async def verify_jwt(
        self,
        token: Union[bytes, str],
        decrypter: IKeychain | None,
        compact_only: bool = False,
        audience: str | None = None
    ) -> JSONWebToken:
        """Verifies a JSON Web Token (JWT) using the public key of the
        client.

        Args:
            token (byte-sequence or string): the JWT to deserialize and
                verify.
            decrypter: a :class:`~IKeychain` implementation that has the
                private keys to decrypt, if the payload is a JWE.
            compact_only (bool): indicates if only compact deserialization
                is allowed. If `compact_only` is ``True`` and the token
                is not compact serialized, an exception is raised.

        Returns
            A :class:`dict` containing the claims in the JWT.
        """
        raise NotImplementedError