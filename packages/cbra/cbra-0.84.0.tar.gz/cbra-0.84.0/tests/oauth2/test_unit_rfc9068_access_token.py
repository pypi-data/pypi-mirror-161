# pylint: skip-file
# type: ignore
import typing

import pytest
from httpx import AsyncClient

from cbra import Application
from cbra.ext.oauth2 import ClientConfig
from cbra.ext.oauth2.types import GrantType
from .rfc9068resource import RFC9068Resource
from .servertest import ServerTest
from .tokenmixin import TokenMixin


class JWTAssertionMixin(ServerTest, TokenMixin):
    url: str = '/resources/1'

    @pytest.fixture
    def clients_available(self):
        return {
            'jwt': ClientConfig(
                client_id='jwt',
                grant_types_supported=[
                    GrantType.jwt_bearer.value
                ]
            )
        }

    @pytest.fixture
    def handlers(self) -> typing.List[typing.Any]:
        return [(RFC9068Resource, '/')]


class TestAccessToken(JWTAssertionMixin):

    @pytest.mark.asyncio
    async def test_missing_token_allows_no_access(self, client: AsyncClient):
        response = await client.get(url=self.url)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_valid_token_allows_access(self, client: AsyncClient, token: str):
        response = await client.get(
            url=self.url,
            headers={'Authorization': f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text


class TestAccessTokenWithoutScope(JWTAssertionMixin):
    default_scope = set()

    @pytest.mark.asyncio
    async def test_rejects_token(self, client: AsyncClient, token: str):
        response = await client.get(
            url=self.url,
            headers={'Authorization': f"Bearer {token}"}
        )
        assert response.status_code == 403, response.text


class TestAccessTokenDifferentScope(JWTAssertionMixin):
    default_scope = {"foo"}

    @pytest.mark.asyncio
    async def test_rejects_token(self, client: AsyncClient, token: str):
        response = await client.get(
            url=self.url,
            headers={'Authorization': f"Bearer {token}"}
        )
        assert response.status_code == 403, response.text



class TestAccessTokenExtraScope(JWTAssertionMixin):
    default_scope = {"foo", "read"}

    @pytest.mark.asyncio
    async def test_accepts_token(self, client: AsyncClient, token: str):
        response = await client.get(
            url=self.url,
            headers={'Authorization': f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
