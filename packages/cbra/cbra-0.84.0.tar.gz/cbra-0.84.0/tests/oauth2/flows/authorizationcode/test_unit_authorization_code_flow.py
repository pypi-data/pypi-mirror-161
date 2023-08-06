# pylint: skip-file
import httpx
import pytest

from ...servertest import ServerTest
from .iauthorizationcodeflow import IAuthorizationCodeFlow


class TestAuthorizationCodeFlow(IAuthorizationCodeFlow, ServerTest):
    client_id: str = 'test-authorization-code-flow'
    cors_url: str = ServerTest.authorize_url
    redirects: bool = True
    response_type: str = "code"

    @pytest.mark.asyncio
    async def test_request_and_request_uri_are_mutually_exclusive(
        self,
        client: httpx.AsyncClient
    ):
        await self.create_authorize_response(
            client=client,
            params={
                'client_id': self.client_id,
                'request_uri': 'foo',
                'request': 'bar'
            },
            status_code=400,
            error="invalid_request"
        )


class TestAuthorizationCodeFlowCORS(TestAuthorizationCodeFlow):
    origin = "https://allowed-cors-domain.example"
    redirects: bool = True