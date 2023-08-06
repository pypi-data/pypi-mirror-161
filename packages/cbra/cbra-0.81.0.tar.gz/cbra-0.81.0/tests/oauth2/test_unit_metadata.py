# pylint: skip-file
import httpx
import pytest
import pytest_asyncio
from ckms.core import Keychain

from cbra import Application
from cbra.ext.oauth2 import AuthorizationServer


class TestMetadataEndpoint:
    metadata_url: str = '/.well-known/oauth-authorization-server'

    @pytest_asyncio.fixture # type: ignore
    async def app(
        self,
        server: AuthorizationServer,
        keychain: Keychain
    ) -> Application:
        await keychain
        app = Application(
            keychain=keychain
        )
        app.add(server, base_path='/oauth2') # type: ignore
        await app.on_startup()
        await server.setup_authorization_server()
        return app

    @pytest.mark.asyncio
    async def test_get_metadata(self, client: httpx.AsyncClient):
        response = await client.get(self.metadata_url) # type: ignore
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_metadata_endpoint_accepts_origin(self, client: httpx.AsyncClient):
        origin = "https://www.example.com"
        response = await client.get( # type: ignore
            url=self.metadata_url,
            headers={'Origin': origin}
        )
        assert response.status_code == 200
        assert response.headers.get('access-control-allow-methods') == "GET"
        assert response.headers.get('access-control-allow-origin') == origin