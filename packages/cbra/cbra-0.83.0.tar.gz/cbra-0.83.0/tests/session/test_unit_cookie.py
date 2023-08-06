# pylint: skip-file
from typing import AsyncGenerator

import fastapi
import pytest
import pytest_asyncio
from ckms.types import JSONWebToken
from ckms.types import MalformedPayload
from httpx import AsyncClient

from cbra import Application
from cbra.session import CookieSession
from cbra.session.const import SESSION_COOKIE_NAME


async def get(session: CookieSession = fastapi.Depends()):
    """Returns the claims that are currently in the session."""
    await session # type: ignore
    return session.claims


@pytest.fixture
def server(app: Application) -> Application:
    app.add_api_route(path='/get', endpoint=get)
    return app


@pytest_asyncio.fixture # type: ignore
async def client(server: Application) -> AsyncGenerator[AsyncClient, None]:
    params = {
        'app': server,
        'base_url': "https://cbra.localhost"
    }
    async with AsyncClient(**params) as client:
        yield client


@pytest_asyncio.fixture # type: ignore
async def session_cookie(client: AsyncClient) -> str:
    response = await client.get('/get') # type: ignore
    return response.cookies[SESSION_COOKIE_NAME]


@pytest.mark.asyncio
async def test_session_is_created(client: AsyncClient):
    response = await client.get('/get') # type: ignore
    claims = response.json()
    assert SESSION_COOKIE_NAME in response.cookies
    assert 'iat' in claims
    assert len(claims) == 1


@pytest.mark.asyncio
async def test_session_is_created_on_malformed(client: AsyncClient):
    response = await client.get( # type: ignore
        url='/get',
        cookies={
            SESSION_COOKIE_NAME: 'foo'
        }
    )
    claims = response.json()
    assert SESSION_COOKIE_NAME in response.cookies
    assert 'iat' in claims
    assert len(claims) == 1


@pytest.mark.asyncio
async def test_session_is_persisted(client: AsyncClient):
    response = await client.get('/get') # type: ignore
    claims = response.json()
    assert SESSION_COOKIE_NAME in response.cookies
    assert 'iat' in claims
    assert len(claims) == 1
    iat = claims['iat']
    response = await client.get('/get') # type: ignore
    claims = response.json()
    assert iat == claims.get('iat')


@pytest.mark.asyncio
async def test_server_can_decode_session(
    server: Application,
    session_cookie: str
):
    _, jwt = await server.codec.jwt(
        session_cookie.encode(),
        accept="jwt+session"
    )
    claims = jwt.dict()
    assert isinstance(jwt, JSONWebToken)
    assert 'iat' in claims
    assert len(claims) == 1


@pytest.mark.asyncio
async def test_server_requires_typed_jwt(
    server: Application,
    session_cookie: str
):
    with pytest.raises(MalformedPayload):
        await server.codec.jwt(
            session_cookie.encode(),
            accept="jwt"
        )