# pylint: skip-file
from typing import AsyncGenerator

import google.oauth2.id_token
import google.auth.transport.requests
import pytest
import pytest_asyncio
from httpx import AsyncClient

from cbra import Application
from examples.google import get_asgi_application


def get_id_token(audience: str) -> str:
    request = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token( # type: ignore
        request=request,
        audience=audience
    )
    return str(id_token) # type: ignore


@pytest.fixture(scope='session')
def id_token(base_url: str) -> str:
    return get_id_token(base_url)


@pytest_asyncio.fixture # type: ignore
async def app() -> Application:
    app = get_asgi_application()
    await app.on_startup()
    return app


@pytest_asyncio.fixture # type: ignore
async def client(
    app: Application,
    base_url: str
) -> AsyncGenerator[AsyncClient, None]:
    params = {
        'app': app,
        'base_url': base_url
    }
    async with AsyncClient(**params) as client:
        yield client
