"""Declares :class:`PushedAuthorizationRequest`."""
from typing import Any

import pydantic
from ckms.types import JSONWebKey

from .baseauthorizationrequest import BaseAuthorizationRequest
from .iclient import IClient
from .iclientrepository import IClientRepository


_BaseParams = BaseAuthorizationRequest.body(
    exclude=['request', 'request_uri']
)


class JAR(_BaseParams):

    issuer: str = pydantic.Field(
        default=...,
        alias='iss',
        title="Issuer",
        description=(
            "The identifier of the client that is requesting "
            "authorization."
        )
    )

    audience: str | set[str] = pydantic.Field(
        default=...,
        alias='aud',
        title="Audience",
        description=(
            "Indicates the audience of the request. Must equal "
            "the `issuer` as specified by the authorization servers' "
            "metadata."
        )
    )

    access_token: str | None = pydantic.Field(
        default=None,
        title="Access token",
        description=(
            "An RFC 9068 access token that identifies the resource owner "
            "on during the **Authorization Code Flow**. This parameter "
            "**must not** be included in requests to the authorization "
            "endpoint; and may only be provided as part of a pushed "
            "authorization request."
        )
    )

    id_token: str | None = pydantic.Field(
        default=None,
        title="ID Token",
        description=(
            "An OpenID Connect ID Token that identifies the resource owner "
            "on during the **Authorization Code Flow**. This parameter "
            "**must not** be included in requests to the authorization "
            "endpoint; and may only be provided as part of a pushed "
            "authorization request."
        )
    )

    encryption_key: JSONWebKey | None = pydantic.Field(
        default=None,
        title="Encryption key",
        description=(
            "A public JSON Web Key (JWK) that is used to encrypt the response "
            "from the **Token Endpoint**."
        )
    )

    def get_claims(self) -> dict[str, Any]:
        return super().get_claims()

    async def get_client(self, clients: IClientRepository) -> IClient:
        """Return a :class:`~cbra.ext.oauth2.types.IClient` implementation
        determined from the request parameters.
        """
        return await clients.get(self.client_id)
