# pylint: skip-file
# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ping(
    client: AsyncClient
) -> None:
    response = await client.post( # type: ignore
        url='/',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        content=b'webhook_id=1'
    )
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_ping_invalid_schema(
    client: AsyncClient
) -> None:
    response = await client.post( # type: ignore
        url='/',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        content=b'foo_id=1'
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ping_invalid_value(
    client: AsyncClient
) -> None:
    response = await client.post( # type: ignore
        url='/',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        content=b'webhook_id=a'
    )
    assert response.status_code == 422