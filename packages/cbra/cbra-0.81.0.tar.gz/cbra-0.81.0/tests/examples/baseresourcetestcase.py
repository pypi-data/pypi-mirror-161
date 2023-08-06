# pylint: skip-file
import itertools
import json
import typing
import urllib.parse

import httpx
import pytest
import pytest_asyncio
import yaml

import cbra
from examples.resource import get_asgi_application
from examples.resource import BarExampleResourceModel
from examples.resource import ExampleResource
from examples.resource import FooExampleResourceModel


VALID_REQUESTS = [
    BarExampleResourceModel(bar=1),
    FooExampleResourceModel(foo=2)
]

SUPPORTED_CONTENT_TYPES = [
    ("application/json", json.dumps),
    ("application/yaml", yaml.safe_dump),
    ("application/x-www-form-urlencoded", urllib.parse.urlencode),
]


class ResourceTestCase:
    allowed_detail_metdhods: typing.Set[str] = {
        "GET",
        "PATCH",
        "PUT",
        "DELETE",
        "OPTIONS"
    }
    allowed_list_methods: typing.Set[str] = {
        "POST",
        "GET",
        "DELETE",
        "OPTIONS"
    }
    detail_url: str = '/resources/1'
    list_url: str = '/resources'
    path_params = {
        'id': 1
    }

    @pytest.fixture
    def app(self) -> cbra.Application:
        return get_asgi_application()

    @pytest_asyncio.fixture # type: ignore
    async def client(
        self,
        app: cbra.Application
    ) -> typing.AsyncGenerator[httpx.AsyncClient, None]:
        params = {
            'base_url': "https://cbra.localhost",
            'headers': {
                'Accept': "application/json"
            }
        }
        async with httpx.AsyncClient(app=app, **params) as c:
            yield c

    @pytest.mark.parametrize("method", allowed_detail_metdhods)
    @pytest.mark.asyncio
    async def test_resource_handle_coerces_parameters(
        self,
        client: httpx.AsyncClient,
        method: str
    ):
        response = await client.get(self.detail_url)
        assert response.status_code == 200, response.text
        dto = response.json()
        assert 'id' in dto
        assert isinstance(dto['id'], int)

    @pytest.mark.parametrize("method", allowed_detail_metdhods)
    @pytest.mark.asyncio
    async def test_resource_handle_sees_parameters(
        self,
        client: httpx.AsyncClient,
        method: str
    ):
        response = await client.get(self.detail_url)
        assert response.status_code == 200
        dto = response.json()
        assert 'path_params' in dto
        assert set(dto['path_params'].keys()) == set(self.path_params.keys())


    @pytest.mark.parametrize("method", allowed_list_methods)
    @pytest.mark.asyncio
    async def test_list_handle_sees_parameters(
        self,
        client: httpx.AsyncClient,
        method: str
    ):
        response = await client.get(self.list_url)
        assert response.status_code == 200, response.text
        dto = response.json()
        assert 'path_params' in dto
        seen = set(dto['path_params'].keys())
        available = set(self.path_params.keys())
        assert seen < available, dto
        assert len(seen) == len(available) - 1

    @pytest.mark.asyncio
    async def test_options_list_exists(
        self,
        client: httpx.AsyncClient,
    ):
        response = await client.options(self.list_url)
        assert response.status_code == 200, response.status_code
        assert 'Allow' in response.headers, response.headers
        allowed = set([x.strip() for x in response.headers['Allow'].split(',')])
        assert allowed == self.allowed_list_methods, allowed

    @pytest.mark.asyncio
    async def test_options_detail_exists(
        self,
        client: httpx.AsyncClient,
    ):
        response = await client.options(self.detail_url)
        assert response.status_code == 200
        allowed = set([x.strip() for x in response.headers['Allow'].split(',')])
        assert allowed == self.allowed_detail_metdhods, allowed

    @pytest.mark.parametrize("dto", [
        BarExampleResourceModel(bar=1),
        FooExampleResourceModel(foo=2),
    ])
    @pytest.mark.asyncio
    async def test_create_multiple_example(
        self,
        client: httpx.AsyncClient,
        dto: typing.Union[BarExampleResourceModel, FooExampleResourceModel]
    ):
        response = await client.post(
            url=self.list_url,
            json=dto.dict()
        )
        result = response.json()
        assert response.status_code == 201
        assert 'dto' in result
        assert dto.dict() == result['dto']

    @pytest.mark.parametrize("dto", [
        BarExampleResourceModel(bar=1),
        FooExampleResourceModel(foo=2),
    ])
    @pytest.mark.asyncio
    async def test_replace_multiple_example(
        self,
        client: httpx.AsyncClient,
        dto: typing.Union[BarExampleResourceModel, FooExampleResourceModel]
    ):
        response = await client.put(
            url=self.detail_url,
            json=dto.dict()
        )
        result = response.json()
        assert response.status_code == 200
        assert 'dto' in result
        assert dto.dict() == result['dto']

    @pytest.mark.parametrize("dto", [
        {'123': 'abc'},
        []
    ])
    @pytest.mark.asyncio
    async def test_create_rejects_invalid_body(
        self,
        client: httpx.AsyncClient,
        dto: typing.Any
    ):
        response = await client.post(
            url=self.list_url,
            json=dto
        )
        assert response.status_code == 422

    @pytest.mark.parametrize("dto", [
        {'123': 'abc'},
        []
    ])
    @pytest.mark.asyncio
    async def test_replace_rejects_invalid_body(
        self,
        client: httpx.AsyncClient,
        dto: typing.Any
    ):
        response = await client.put(
            url=self.detail_url,
            json=dto
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_query_parses_parameters(
        self,
        client: httpx.AsyncClient
    ):
        pytest.skip()
        params = ExampleResource.query(foo=1, bar=2, baz=['3', '4'])
        response = await client.get(
            url=self.list_url,
            params=params.dict()
        )
        assert response.status_code == 200