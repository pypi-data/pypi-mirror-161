"""Declares :class:`CorsMixin`."""
import httpx
import pytest


class CorsMixin:
    cors_url: str
    cors_allowed_methods: set[str]
    cors_allowed_origin: str

    def get_cors_url(self) -> str:
        return self.cors_url

    @pytest.mark.asyncio
    async def test_preflight(self, client: httpx.AsyncClient, origin: str | None = None):
        origin = origin or self.cors_allowed_origin
        headers = {
            'Origin': origin,
            'Access-Control-Request-Methods': str.join(',', self.cors_allowed_methods)
        }
        response = await client.options( # type: ignore
            url=self.get_cors_url(),
            headers=headers
        )
        allowed_methods = ','.join(sorted(self.cors_allowed_methods | {"OPTIONS"}))
        assert response.status_code == 200, response.status_code
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == origin, response.headers
        assert response.headers['Access-Control-Allow-Methods'] == allowed_methods, response.headers

    @pytest.mark.asyncio
    async def test_preflight_accepts_none_whitelisted_domain(
        self,
        client: httpx.AsyncClient
    ):
        await self.test_preflight(client, "https://foo.invalid")