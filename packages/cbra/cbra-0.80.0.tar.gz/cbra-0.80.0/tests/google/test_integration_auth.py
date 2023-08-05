# pylint: skip-file
# Copyright (C) 2022 Cochise Ruhulessin <cochiseruhulessin@gmail.com>
# 
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
import pytest
from ckms.jose import PayloadCodec
from ckms.types import JSONWebToken
from httpx import AsyncClient

from cbra import Application
from examples.google import ExampleGoogleEndpoint
from .conftest import get_id_token


@pytest.mark.asyncio
async def test_authenticate_with_token(
    id_token: str,
    client: AsyncClient
):
    _, claims = await PayloadCodec().jwt(id_token)
    response = await client.post( # type: ignore
        url='/',
        headers={'Authorization': f'Bearer {id_token}'}
    )
    dto = response.json()
    assert isinstance(claims, JSONWebToken)
    assert response.status_code == 200
    assert dto.get('email') == claims.extra.get('email')


@pytest.mark.asyncio
async def test_bearer_token_is_required(
    client: AsyncClient
):
    response = await client.post( # type: ignore
        url='/'
    )
    dto = response.json()
    assert response.status_code == 401
    assert dto['spec']['code'] == 'AUTHENTICATION_REQUIRED'


@pytest.mark.asyncio
async def test_invalid_audience_is_rejected(
    client: AsyncClient
):
    id_token = get_id_token("https://example.com")
    response = await client.post( # type: ignore
        url='/',
        headers={'Authorization': f'Bearer {id_token}'}
    )
    dto = response.json()
    assert response.status_code == 403
    assert dto['spec']['code'] == "WRONG_AUDIENCE"


@pytest.mark.asyncio
async def test_invalid_scheme_is_rejected(
    id_token: str,
    client: AsyncClient
):
    response = await client.post( # type: ignore
        url='/',
        headers={'Authorization': f'Basic {id_token}'}
    )
    dto = response.json()
    assert response.status_code == 403
    assert dto['spec']['code'] == "INVALID_AUTHORIZATION_SCHEME"


@pytest.mark.asyncio
async def test_no_whitelisted_service_accounts_returns_403(
    app: Application,
    id_token: str,
    client: AsyncClient
):
    Endpoint = ExampleGoogleEndpoint.new( # type: ignore
        service_accounts=set()
    )
    app.add(Endpoint, base_path='/whitelisted')
    response = await client.post( # type: ignore
        url='/whitelisted',
        headers={'Authorization': f'Bearer {id_token}'}
    )
    dto = response.json()
    assert response.status_code == 403
    assert dto['spec']['code'] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_different_whitelisted_service_accounts_returns_403(
    app: Application,
    id_token: str,
    client: AsyncClient
):
    Endpoint = ExampleGoogleEndpoint.new( # type: ignore
        service_accounts={"foo@bar.baz"}
    )
    app.add(Endpoint, base_path='/whitelisted')
    response = await client.post( # type: ignore
        url='/whitelisted',
        headers={'Authorization': f'Bearer {id_token}'}
    )
    dto = response.json()
    assert response.status_code == 403
    assert dto['spec']['code'] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_allow_unauthenticated(
    app: Application,
    id_token: str,
    client: AsyncClient
):
    Endpoint = ExampleGoogleEndpoint.new( # type: ignore
        require_authentication=False
    )
    app.add(Endpoint, base_path='/no-authentication')
    response = await client.post( # type: ignore
        url='/no-authentication',
    )
    dto = response.json()
    assert response.status_code == 200
    assert dto.get('email') == "none"