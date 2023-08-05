# pylint: skip-file
import typing

import httpx
from ckms.jose import PayloadCodec
from ckms.types import JSONWebToken


class JARMixin:
    base_url: str
    client_id: str
    jar_url: str

    async def create_jar_response(
        self,
        *,
        params: dict[str, typing.Any],
        codec: PayloadCodec,
        client: httpx.AsyncClient,
        algorithm: str = 'EdDSA',
        using: str = 'sig',
        headers: dict[str, str] | None = None
    ) -> tuple[str, str]:
        """Create a request to the authorization endpoint."""
        response = await client.post( # type: ignore
            url=self.jar_url,
            content=await self.create_jar(
                codec=codec,
                params=params,
                algorithm=algorithm,
                using=using
            ),
            headers={
                'Content-Type': "application/oauth-authz-req+jwt",
                **(headers or {})
            }
        )
        response.raise_for_status()
        assert response.status_code in {200, 201}, response.text
        dto = response.json()
        assert 'request_uri' in dto
        assert 'expires_in' in dto
        assert isinstance(dto['expires_in'], int)
        return dto['request_uri'], dto['expires_in']

    async def create_jar(
        self,
        *,
        codec: PayloadCodec,
        params: dict[str, typing.Any],
        algorithm: str = 'EdDSA',
        using: str = 'sig'
    ) -> str:
        """Creates a JWT-Secured Authorization Request."""
        return await self.serialize_jar(
            codec=codec,
            payload=JSONWebToken.strict(**{
                'iss': self.client_id,
                'aud': self.base_url,
                'client_id': self.client_id,
                'ttl': 120,
                **params
            }),
            using=using
        )

    async def serialize_jar(
        self,
        codec: PayloadCodec,
        payload: JSONWebToken,
        using: str
    ) -> str:
        """Serializes the payload of the JWT-Secured Authorization
        Request.
        """
        return await codec.encode(
            payload,
            signers=[using],
            content_type="oauth-authz-req+jwt"
        )