# pylint: skip-file
import httpx
import pytest

import cbra
from cbra.const import REQUEST_METHODS
from examples.cors import get_asgi_application
from examples.cors import ExampleCorsPolicy


ALLOWED_HEADERS = ExampleCorsPolicy.allowed_headers
ALLOWED_METHODS = REQUEST_METHODS & ExampleCorsPolicy.allowed_methods
FORBIDDEN_HEADERS = {'X-Foo', 'X-Bar'}
FORBIDDEN_METHODS = REQUEST_METHODS - ALLOWED_METHODS
ORIGIN = "https://unimatrixone.local"


@pytest.fixture
def app() -> cbra.Application:
    ExampleCorsPolicy.allowed_origins.add(ORIGIN)
    return get_asgi_application()


@pytest.mark.parametrize("method", sorted(ALLOWED_METHODS))
@pytest.mark.asyncio
async def test_allowed_methods_are_accepted_by_options(client: httpx.AsyncClient, method: str):
    response = await client.options(
        url='/',
        headers={
            'Origin': ORIGIN,
            'Access-Control-Request-Methods': method
        }
    )
    assert response.status_code == 200
    assert 'Access-Control-Allow-Credentials' in response.headers
    assert 'Access-Control-Allow-Headers' in response.headers
    assert 'Access-Control-Allow-Methods' in response.headers
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == ORIGIN


@pytest.mark.parametrize("header", sorted(ALLOWED_HEADERS))
@pytest.mark.asyncio
async def test_allowed_methods_are_accepted_by_options(client: httpx.AsyncClient, header: str):
    response = await client.options(
        url='/',
        headers={
            'Origin': ORIGIN,
            'Access-Control-Request-Headers': header
        }
    )
    assert response.status_code == 200
    assert 'Access-Control-Allow-Credentials' in response.headers
    assert 'Access-Control-Allow-Headers' in response.headers
    assert 'Access-Control-Allow-Methods' in response.headers
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == ORIGIN
    assert header in response.headers['Access-Control-Allow-Headers']


@pytest.mark.parametrize("method", sorted(ALLOWED_METHODS))
@pytest.mark.asyncio
async def test_allowed_methods_are_accepted(client: httpx.AsyncClient, method: str):
    response = await getattr(client, method.lower())(
        url='/',
        headers={'Origin': ORIGIN}
    )
    assert response.status_code == 200
    assert 'Access-Control-Allow-Credentials' in response.headers, response.headers
    assert 'Access-Control-Expose-Headers' in response.headers
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == ORIGIN


@pytest.mark.parametrize("header", sorted(ALLOWED_HEADERS))
@pytest.mark.asyncio
async def test_allowed_headers_are_accepted(client: httpx.AsyncClient, header: str):
    response = await client.get(
        url='/',
        headers={'Origin': ORIGIN, header: 'Foo'}
    )
    assert response.status_code == 200
    assert 'Access-Control-Allow-Credentials' in response.headers, response.headers
    assert 'Access-Control-Expose-Headers' in response.headers
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == ORIGIN
    assert header in response.headers['Access-Control-Expose-Headers']


@pytest.mark.parametrize("method", sorted(FORBIDDEN_METHODS))
@pytest.mark.asyncio
async def test_forbidden_methods_are_rejected_by_options(client: httpx.AsyncClient, method: str):
    response = await client.options(
        url='/',
        headers={
            'Origin': ORIGIN,
            'Access-Control-Request-Methods': method
        }
    )
    assert response.status_code == 200
    assert 'Access-Control-Allow-Credentials' in response.headers
    assert 'Access-Control-Allow-Headers' in response.headers
    assert 'Access-Control-Allow-Methods' in response.headers
    assert 'Access-Control-Allow-Origin' in response.headers
    assert 'Access-Control-Max-Age' in response.headers
    assert method not in response.headers['Access-Control-Allow-Methods']


@pytest.mark.parametrize("header", sorted(FORBIDDEN_HEADERS))
@pytest.mark.asyncio
async def test_forbidden_headers_are_rejected_by_options(client: httpx.AsyncClient, header: str):
    response = await client.options(
        url='/',
        headers={
            'Origin': ORIGIN,
            'Access-Control-Request-Headers': header
        }
    )
    assert response.status_code == 200
    assert 'Access-Control-Allow-Credentials' in response.headers
    assert 'Access-Control-Allow-Headers' in response.headers
    assert 'Access-Control-Allow-Methods' in response.headers
    assert 'Access-Control-Allow-Origin' in response.headers
    assert 'Access-Control-Max-Age' in response.headers
    assert header not in response.headers['Access-Control-Allow-Headers']


@pytest.mark.asyncio
async def test_forbidden_origin_is_rejected_by_options(client: httpx.AsyncClient):
    response = await client.options(
        url='/',
        headers={
            'Origin': "https://example.com",
        }
    )
    assert response.status_code == 200
    assert 'Access-Control-Allow-Credentials' not in response.headers
    assert 'Access-Control-Allow-Headers' not in response.headers
    assert 'Access-Control-Allow-Methods' not in response.headers
    assert 'Access-Control-Allow-Origin' not in response.headers
    assert 'Access-Control-Max-Age' not in response.headers


@pytest.mark.parametrize("method", ALLOWED_METHODS)
@pytest.mark.asyncio
async def test_no_origin_allows_all_methods(client: httpx.AsyncClient, method: str):
    response = await getattr(client, method.lower())(
        url='/'
    )
    assert response.status_code == 200
    assert 'Access-Control-Allow-Credentials' not in response.headers
    assert 'Access-Control-Allow-Headers' not in response.headers
    assert 'Access-Control-Allow-Methods' not in response.headers
    assert 'Access-Control-Allow-Origin' not in response.headers
    assert 'Access-Control-Max-Age' not in response.headers


@pytest.mark.parametrize("method", ALLOWED_METHODS)
@pytest.mark.asyncio
async def test_same_origin_allows_all_methods(client: httpx.AsyncClient, method: str):
    response = await getattr(client, method.lower())(
        url='/',
        headers={'Origin': str(client.base_url)}
    )
    assert response.status_code == 200
    assert 'Access-Control-Allow-Credentials' not in response.headers
    assert 'Access-Control-Allow-Headers' not in response.headers
    assert 'Access-Control-Allow-Methods' not in response.headers
    assert 'Access-Control-Allow-Origin' not in response.headers
    assert 'Access-Control-Max-Age' not in response.headers