# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pytest

from ckms.jose import PayloadCodec
from ckms.types import IKeySpecification
from ckms.types import JSONWebToken
from ckms.types import JSONWebKeySet
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cors_allows_different_origin(
    client: AsyncClient,
    codec: PayloadCodec,
    reks_url: str
):
    response = await client.get( # type: ignore
        url=reks_url,
        headers={'Origin': 'www.example.com'}
    )
    assert response.status_code == 200, response.content


@pytest.mark.asyncio
async def test_verify_jwks(
    client: AsyncClient,
    codec: PayloadCodec,
    reks_url: str
):
    response = await client.get(reks_url) # type: ignore
    jwt = await codec.decode(response.content, accept={"jwt+reks"})
    assert isinstance(jwt, JSONWebToken)
    assert 'jwks' in jwt.extra


@pytest.mark.asyncio
async def test_post_encrypted_and_signed_body(
    client: AsyncClient,
    codec: PayloadCodec,
    reks_url: str,
    jose_client_signer: IKeySpecification
):
    # Obtain the Request Encryption Key Set (REKS) from the
    # well-known endpoint.
    response = await client.get(reks_url) # type: ignore
    _, jwt = await codec.jwt(response.content, accept={"jwt+reks"})
    jwks = JSONWebKeySet(**jwt.extra['jwks'])


    # Use the REKS to encrypt a JSON Web Signature (JWS) and make
    # a POST request.
    assert jwks.keys
    client_codec = PayloadCodec(
        signing_keys=[jose_client_signer],
        encryption_keys=[x for x in jwks.keys]
    )
    obj = await client_codec.encode(
        payload={'foo': 1}
    )
    response = await client.post( # type: ignore
        url='/',
        content=obj,
        headers={'Content-Type': "application/jwt"}
    )
    dto = response.json()
    assert response.status_code == 200, dto['spec']['message']
    assert dto.get('foo') == 1, dto