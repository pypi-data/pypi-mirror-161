# pylint: skip-file
import json
from os import access
import typing
import urllib.parse

import httpx
import pytest
import yaml

import cbra
from cbra.types import IRenderer
from examples.endpoint import ExampleEndpoint


@pytest.fixture
def endpoint():
    return ExampleEndpoint


@pytest.fixture
def app(endpoint: typing.Type[ExampleEndpoint]):
    app = cbra.Application()
    app.add(endpoint, base_path='/get', method='GET')
    app.add(endpoint, base_path='/post', method='POST')
    return app


@pytest.mark.asyncio
async def test_endpoint_returns_parameter(
    client: httpx.AsyncClient
):
    response = await client.get(
        url='/get',
        headers={'Accept': "application/json"}
    )
    try:
        assert response.json().get('path_param') == None
    except json.JSONDecodeError:
        pytest.fail(response.text)


@pytest.mark.parametrize("renderer", ExampleEndpoint.renderers)
@pytest.mark.asyncio
async def test_content_negotiation_get(
    client: httpx.AsyncClient,
    renderer: typing.Type[IRenderer],
    url: str ='/get'
):
    response = await client.get(
        url=url,
        headers={'Accept': renderer.media_type}
    )
    assert response.status_code == 200
    assert 'Content-Type' in response.headers
    assert response.headers['Content-Type'] == renderer.response_media_type


@pytest.mark.parametrize("accept", [
    "application/*",
    "*/*"
])
@pytest.mark.asyncio
async def test_content_negotiation_wildcard(
    client: httpx.AsyncClient,
    accept: str,
    url: str ='/get'
):
    response = await client.get(
        url=url,
        headers={'Accept': accept}
    )
    assert response.status_code == 200
    assert 'Content-Type' in response.headers
    assert response.headers['Content-Type'] != accept


@pytest.mark.asyncio
async def test_unsupported_media_returns_406(
    client: httpx.AsyncClient,
    url: str = '/get'
):
    response = await client.get(
        url=url,
        headers={'Accept': "application/foo"}
    )
    assert response.headers['Content-Type'] != '*/*'
    assert response.status_code == 406, response.headers


@pytest.mark.asyncio
async def test_unsupported_media_used_default_renderer(
    client: httpx.AsyncClient,
    endpoint: typing.Type[ExampleEndpoint],
    url: str = '/get'
):
    response = await client.get(
        url=url,
        headers={'Accept': "application/foo"}
    )
    assert response.headers.get('Content-Type') == endpoint.fallback_renderer.media_type


@pytest.mark.parametrize("content_type,serialize", [ # type: ignore
    ("application/json", json.dumps),
    ("application/yaml", yaml.safe_dump), # type: ignore
    ("application/x-www-form-urlencoded", urllib.parse.urlencode),
])
@pytest.mark.asyncio
async def test_content_negotiation_with_body(
    client: httpx.AsyncClient,
    content_type: str,
    serialize: typing.Callable[..., str],
    url: str = '/post'
):
    dto = {'foo': 1}
    response = await client.post(
        url=url,
        content=str.encode(serialize(dto)),
        headers={
            'Accept': "application/json",
            'Content-Type': content_type,
        }
    )
    assert response.status_code == 200, response.text
    dto = response.json()
    assert dto.get('body') is not None
    assert int(dto['body'].get('foo')) == 1


@pytest.mark.asyncio
async def test_form_data_post(
    client: httpx.AsyncClient,
    url: str = '/post'
):
    dto = {'foo': 1}
    response = await client.post(
        url=url,
        data=dto,
        headers={'Accept': "application/json"}
    )
    assert response.status_code == 200, response.text
    dto = response.json()
    assert dto.get('body') is not None
    assert dto['body'].get('foo') == '1' # forms have no typing


@pytest.mark.parametrize("wants_digest,name", [
    ("sha-256", "sha-256"),
    ("sha-512", "sha-512"),
    ("sha-256,sha-512", "sha-256"),
    ("sha-256;q=0.5,sha-512;q=1", "sha-512"),
    (None, "sha-256"),
])
@pytest.mark.asyncio
async def test_digest_negotiation(
    client: httpx.AsyncClient,
    wants_digest: typing.Optional[str],
    name: str,
    url: str = '/get'
):
    headers = {}
    if wants_digest:
        headers['Wants-Digest'] = wants_digest
    response = await client.get(
        url,
        headers=headers
    )
    assert response.status_code == 200
    assert 'Digest' in response.headers
    assert str.startswith(response.headers['Digest'], name)


@pytest.mark.asyncio
async def test_digest_unsupported_is_rejected(
    client: httpx.AsyncClient,
    url: str = '/get'
):
    response = await client.get(
        url=url,
        headers={'Wants-Digest': "foo"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_digest_supported_is_selected(
    client: httpx.AsyncClient,
    url: str = '/get'
):
    response = await client.get(
        url=url,
        headers={'Wants-Digest': "foo,sha-256"}
    )
    assert response.status_code == 200, response.text


@pytest.mark.parametrize("wants_digest", [
    'foo;;,bar',
    'foo;q=a'
])
@pytest.mark.asyncio
async def test_digest_invalid_header_is_rejected(
    client: httpx.AsyncClient,
    wants_digest: str,
    url: str = '/get'
):
    response = await client.get(
        url=url,
        headers={'Wants-Digest': wants_digest}
    )
    dto = response.json()
    assert response.status_code == 400
    assert dto['spec']['code'] == 'INVALID_HEADER_VALUE'