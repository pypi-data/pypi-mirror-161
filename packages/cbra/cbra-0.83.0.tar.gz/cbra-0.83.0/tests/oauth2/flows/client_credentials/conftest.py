# pylint: skip-file
import pytest_asyncio
from ckms.core import Keychain
from httpx import AsyncClient

import cbra
from cbra.ext.jwks import JWKSEndpoint
from cbra.ext.oauth2 import AuthorizationServer


base_url: str = "https://cbra-oauth2.localhost"


@pytest_asyncio.fixture # type: ignore
async def app(
    server: AuthorizationServer,
    keychain: Keychain
) -> cbra.Application:
    await keychain
    app = cbra.Application(
        keychain=keychain
    )
    app.add(JWKSEndpoint)
    app.add(server, base_path='/oauth2')
    await app.on_startup()
    return app


@pytest_asyncio.fixture # type: ignore
async def client(app: cbra.Application):
    params = {
        'app': app,
        'base_url': base_url
    }
    async with AsyncClient(**params) as client:
        yield client