# pylint: skip-file
import itertools
import json
import typing
import urllib.parse

import httpx
import pydantic
import pytest
import pytest_asyncio
import yaml

import cbra
from . import BarModel
from . import FooModel
from . import ContentNegotiationEndpoint


SERIALIZE = {
    "application/json": json.dumps,
    "application/yaml": yaml.safe_dump,
    "application/x-www-form-urlencoded": urllib.parse.urlencode
}

SUPPORTED_TYPES = [
    "application/json",
    "application/yaml",
    "application/x-www-form-urlencoded"
]

VALID_REQUESTS = itertools.product(
    SUPPORTED_TYPES,
    [
        FooModel(foo=1),
        BarModel(bar=2)
    ]
)


@pytest.fixture
def app() -> cbra.Application:
    app = cbra.Application()
    app.add(ContentNegotiationEndpoint, base_path='/', method="POST")
    return app


@pytest_asyncio.fixture
async def client(
    app: cbra.Application
) -> typing.AsyncGenerator[httpx.AsyncClient, None]:
    params = {
        'app': app,
        'base_url': "https://cbra.localhost"
    }
    async with httpx.AsyncClient(**params) as c:
        yield c


@pytest.mark.parametrize("content_type,dto", VALID_REQUESTS)
@pytest.mark.asyncio
async def test_content_is_deserialized_and_casted(
    client: httpx.AsyncClient,
    content_type: str,
    dto: pydantic.BaseModel
):
    content: bytes = str.encode(SERIALIZE[content_type](dto.dict()))
    response = await client.post(
        url='/',
        content=content,
        headers={
            'Accept': 'application/json',
            'Content-Type': content_type
        }
    )
    assert response.status_code == 200
    assert response.json() == dto.dict()