# type: ignore
"""An OAuth 2.x client that automatically discovers the servers'
capabilities.
"""
import asyncio
import collections
import datetime
import secrets
from typing import Any

import httpx
import jwcrypto.jwk
import jwcrypto.jwt

from cbra.ext.oauth2.ref.keys import KEY_BOB


OAUTH2_SERVER = "https://localhost:8000"


class SubjectClient(httpx.AsyncClient):
    client_id: str
    default_assertion_ttl: int = 30
    metadata_url: str = "/.well-known/oauth-authorization-server"
    private_key: jwcrypto.jwk.JWK
    subject: str
    _metadata: dict[str, Any] = collections.defaultdict(dict)

    @property
    def jwks_uri(self) -> str | None:
        """The URL of the authorization servers' JWKS."""
        return self._metadata[self.server].get('jwks_uri')

    @property
    def metadata(self) -> dict[str, Any]:
        """The metadata describing the server, as a dictionary."""
        return self._metadata[self.server]

    @property
    def token_endpoint(self) -> str | None:
        """The URL of the authorization servers' token endpoint."""
        return self._metadata[self.server].get('token_endpoint')

    def __init__(
        self,
        server: str,
        client_id: str,
        subject: str,
        private_key: bytes,
        **kwargs: Any
    ):
        super().__init__( # type: ignore
            base_url=server,
            **kwargs
        )
        self.client_id = client_id
        self.server = server
        self.private_key = jwcrypto.jwk.JWK.from_pem(private_key, None) # type: ignore
        self.subject = subject
        self._metadata = SubjectClient._metadata

    def create_assertion(self) -> str:
        """Creates an assertion to retrieve a token from the
        endpoint.
        """
        now = int(datetime.datetime.utcnow().timestamp())
        claims = {
            'jti': secrets.token_urlsafe(24),
            'iss': self.subject,
            'aud': self.token_endpoint,
            'sub': self.subject,
            'iat': now,
            'exp': now + self.default_assertion_ttl,
            'nbf': now,
        }
        token = jwcrypto.jwt.JWT(
            header={'alg': 'EdDSA'},
            claims=claims
        )
        token.make_signed_token(self.private_key)
        return token.serialize()

    async def get_access_token(self, scope: set[str]):
        response = await self.post(
            url=self.token_endpoint,
            json={
                'grant_type': "urn:ietf:params:oauth:grant-type:jwt-bearer",
                'client_id': self.client_id,
                'assertion': self.create_assertion(),
                'scope': str.join(' ', sorted(scope))
            }
        )
        if response.status_code != 200:
            raise Exception(response.text)
        dto = response.json()
        return dto['access_token']

    async def get_server_metadata(self) -> dict[str, Any]:
        """Return a dictionary containing the metadata that was discovered
        from the authorization server.
        """
        response = await self.get(self.metadata_url)
        response.raise_for_status()
        return response.json()

    async def __aenter__(self):
        client = await super().__aenter__()
        if self.server not in self._metadata:
            self._metadata[self.server] = await self.get_server_metadata()
        return self


async def main():
    params = {
        'client_id': 'jwt',
        'server': OAUTH2_SERVER,
        'verify': False,
        'subject': "bob@example.unimatrixone.io",
        'private_key': open(KEY_BOB, 'rb').read()
    }
    async with SubjectClient(**params) as client:
        print(client.token_endpoint)
        print(client.jwks_uri)
        print(client.create_assertion())
        print(await client.get_access_token({"openid", "read"}))


if __name__ == '__main__':
    asyncio.run(main())
