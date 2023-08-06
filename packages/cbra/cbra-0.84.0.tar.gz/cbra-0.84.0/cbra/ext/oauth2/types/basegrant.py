"""Declares :class:`BaseGrant`."""
from cbra.ext.oauth2.types.isubject import ISubject
import pydantic

from .clientassertiontype import ClientAssertionType
from .fields import ResourceField
from .granttype import GrantType
from .iclient import IClient
from .stringorlist import StringOrList


class BaseGrant(pydantic.BaseModel):
    __module__: str = 'cbra.ext.oauth2.types'
    _client: IClient | None = pydantic.PrivateAttr(default=None)

    grant_type: GrantType
    client_id: str | None = pydantic.Field(
        default=None,
        title="Client ID",
        description=(
            "Identifies the client that is requesting a token on the behalf of "
            "the resource owner. If the client is public or does not use the "
            "`Authorization` header to authenticate, this parameter is "
            "mandatory."
        )
    )

    client_secret: str | None = pydantic.Field(
        default=None,
        title="Client secret",
        description=(
            "Required if the client is confidential and the request does not "
            "use the `Authorization` header or other supported scheme to "
            "authenticate, else this parameter must be not present. It may "
            "also be omitted if the client secret is an empty string."
        )
    )

    client_assertion_type: ClientAssertionType | None = pydantic.Field(
        default=None,
        title="Client assertion type",
        description=(
            "The authorization server supports the following client assertions "
            "to establish the identity of confidential OAuth 2.0 clients:\n\n"
            "`urn:ietf:params:oauth:client-assertion-type:jwt-bearer`\n\n"
            "Clients that have registered a public key sign a JWT using that "
            "key. The Client authenticates in accordance with **JSON Web Token "
            "(JWT) Profile for OAuth 2.0 Client Authentication and Authorization "
            "Grants** and **Assertion Framework for OAuth 2.0 Client Authentication "
            "and Authorization Grants**. The JWT must contain the following "
            "required Claim Values and may contain the following optional Claim "
            "Values:\n\n"
            "- `iss` - (Required) Issuer. This MUST contain the ``client_id`` of "
            "the OAuth Client.\n"
            "- `sub` - (Required) Issuer. This MUST contain the ``client_id`` of "
            "the OAuth Client.\n"
            "- `aud` - (Required) Value that identifies the authorization server "
            "as an intended audience. The authorization server must verify that "
            "it is an intended audience for the token. The Audience must be the "
            "URL of the authorization server's **Token Endpoint**.\n"
            "- `jti` - (Required) A unique identifier for the token, which can "
            "be used to prevent reuse of the token. These tokens must only be "
            "used once.\n"
            "- `exp` - (Required) Expiration time on or after which the ID "
            "Token must not be accepted for processing.\n"
            "- `iat` - (Optional) Time at which the JWT was issued."
        )
    )

    client_assertion: str | None = pydantic.Field(
        default=None,
        title="Client assertion",
        description=(
            "The client assertion used to authenticate a confidential OAuth 2.0 "
            "client. See `client_assertion_type` for the supported protocols and "
            "formats."
        )
    )

    resource: StringOrList = ResourceField()

    def get_audience(self) -> str | list[str] | None:
        """Return the audience to use when issueing a JWT access token
        as a result of the request.
        """
        return list(sorted(self.resource or []))

    def get_client(self) -> IClient:
        assert self._client is not None # nosec
        return self._client

    def has_client_assertion(self) -> bool:
        """Return a boolean indicating if the client authenticates itself
        using a client assertion.
        """
        return bool(self.client_assertion_type)\
            and bool(self.client_assertion)\
            and bool(self.client_id)

    def set_client(self, client: IClient) -> None:
        self._client = client

    def validate_grant(self, client: IClient, subject: ISubject | None) -> None:
        pass