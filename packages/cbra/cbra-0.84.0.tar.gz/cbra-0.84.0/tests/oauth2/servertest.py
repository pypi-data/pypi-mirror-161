# type: ignore
"""Declares :class:`ServerTest`."""
import typing
import urllib.parse

import cbra
import fastapi
import pytest
import pytest_asyncio
import unimatrix.lib.http
from ckms.core import Keychain
from ckms.jose import PayloadCodec
from ckms.types import JSONWebToken
from httpx import AsyncClient
from httpx import Response

from cbra.ext.jwks import JWKSEndpoint
from cbra.ext.oauth2 import AuthorizationEndpoint
from cbra.ext.oauth2 import ConfigFileClientRepository
from cbra.ext.oauth2 import MemoryClientRepository
from cbra.ext.oauth2 import MemoryStorage
from cbra.ext.oauth2 import MemorySubjectRepository
from cbra.ext.oauth2 import AuthorizationServer
from cbra.ext.oauth2 import RFC9068Principal
from cbra.ext.oauth2 import TokenRequestHandler
from cbra.ext.oauth2 import TokenIssuer
from cbra.ext.oauth2 import ref
from cbra.ext.oauth2.types import IClient
from cbra.ext.oauth2.types import IClientRepository
from cbra.ext.oauth2.types import ISubject
from cbra.ext.oauth2.types import ISubjectRepository
from cbra.types import IPrincipal


class ServerTest:
    base_url: str = "https://cbra-oauth2.localhost"
    authorize_url: str = f'{base_url}/oauth2/authorize'
    authorize_status_code: int = 303
    token_url: str = f'{base_url}/oauth2/token'
    redirect_uri: str = f"{base_url}/callback"
    jar_url: str = f"{base_url}/oauth2/par"
    message: str = "Hello world!"
    client_id: str = None

    @pytest.fixture
    def handlers(self) -> typing.List[typing.Any]:
        return []

    @pytest_asyncio.fixture
    async def app(
        self,
        server: AuthorizationServer,
        handlers: typing.List[typing.Any],
        keychain: Keychain
    ) -> cbra.Application:
        await keychain
        app = cbra.Application(
            keychain=keychain
        )
        app.add_api_route('/rfc9068', endpoint=self.handle_rfc9068_token)
        app.add(server, base_path='/oauth2')
        for handler_class, base_path in handlers:
            app.add(handler_class, base_path=base_path)
        await app.on_startup()
        await server.setup_authorization_server()
        return app

    def assert_error(self, response: Response, error: str, status_code: int = 400):
        assert response.status_code == status_code, response.status_code
        assert response.json()['error'] == error, response.json()

    def assert_redirects(self, response: Response, uri: str):
        u1 = urllib.parse.urlparse(response.headers['Location'])
        u2 = urllib.parse.urlparse(uri)
        assert u1[:3] == u2[:3]

    def assert_query_parameter(self, url: str, name: str, value: str):
        p = urllib.parse.urlparse(url)
        q = unimatrix.lib.http.parse_qs(p.query)
        assert name in q, f'{name} not in {repr(q)}'
        assert q[name] == value

    async def get_current_client(self) -> IClient:
        return ConfigFileClientRepository().get(self.client_id)

    async def get_client_keychain(self, key: str) -> Keychain:
        keychain = Keychain()
        keychain.configure({
            'sig': {
                'provider': "local",
                'kty': "OKP",
                'alg': "EdDSA",
                'key': {'path': f"pki/{key}.key"},
                'crv': "Ed448",
                'use': 'sig'
            }
        })
        await keychain
        return keychain

    async def get_client_codec(
        self,
        keychain: Keychain
    ) -> PayloadCodec:
        return PayloadCodec(
            signer=keychain
        )

    async def handle_rfc9068_token(
        self,
        principal: IPrincipal = fastapi.Depends(RFC9068Principal())
    ):
        assert principal.has_scope("read")
        return {"message": self.message}

    def assert_rfc9068(self, token: str, claim: str, value: typing.Any):
        header, payload, signature = str.split(token, '.')
        jwt = JSONWebToken.frompayload(payload)
        claims = jwt.dict()
        assert claim in claims
        assert claims[claim] == value
