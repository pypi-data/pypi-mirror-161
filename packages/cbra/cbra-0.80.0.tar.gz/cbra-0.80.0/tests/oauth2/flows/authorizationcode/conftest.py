# pylint: skip-file
import typing

import pytest
import pytest_asyncio
from ckms.core import Keychain
from httpx import AsyncClient

import cbra
from cbra.ext.oauth2 import AuthorizationServer
from cbra.ext.oauth2.types import ISubject


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
    app.add(server, base_path='/oauth2') # type: ignore
    await app.on_startup()
    return app


@pytest.fixture
def client_kwargs(app: cbra.Application, bob: ISubject) -> dict[str, typing.Any]:
    return {
        'app': app,
        'base_url': base_url,
        'cookies': {
            'subject': bob.sub
        }
    }


@pytest_asyncio.fixture # type: ignore
async def client(client_kwargs: dict[str, typing.Any]):
    async with AsyncClient(**client_kwargs) as client:
        yield client