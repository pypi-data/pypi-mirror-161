# pylint: skip-file
import typing
import urllib.parse

import httpx

from ...assertedclientmixin import AssertedClientMixin
from ...jarmixin import JARMixin
from ...servertest import ServerTest
from .iauthorizationcodeflow import IAuthorizationCodeFlow


class TestJARFlow(ServerTest, JARMixin, IAuthorizationCodeFlow, AssertedClientMixin):
    client_id: str = 'test-jar'
    client_key: str = 'confidential1'
    cors_allowed_methods: set[str] = {"POST"}
    cors_url: str = ServerTest.jar_url
    redirects: bool = False
    response_type: str = "code"

    async def get_token_client_params(self) -> dict[str, typing.Any]:
        return {
            'client_id': self.client_id,
            'client_assertion_type': self.assertion_type,
            'client_assertion': await self.get_client_assertion(
                keychain=await self.get_client_keychain(self.client_key),
                sub=self.client_id
            )
        }

    async def create_authorize_response(
        self,
        client: httpx.AsyncClient,
        params: dict[str, str],
        status_code: int = 303,
        error: str | None = None,
        headers: dict[str, str] | None = None
    ) -> tuple[urllib.parse.ParseResult, dict[str, str], dict[str, str]]:
        try:
            request_uri, _ = await self.create_jar_response(
                client=client,
                params=params,
                codec=await self.get_client_codec(
                    keychain=await self.get_client_keychain(self.client_key)
                ),
                headers=headers
            )
        except httpx.HTTPStatusError as exception:
            if error is None:
                raise
            dto = exception.response.json()
            assert exception.response.status_code == status_code
            assert dto.get('error') == error
            return (urllib.parse.urlparse(''), dict(exception.response.headers), {})

        params = {
            'client_id': self.client_id,
            'request_uri': request_uri
        }
        return await super().create_authorize_response(client, params, status_code, error)


class TestJARFlowCORS(TestJARFlow):
    origin = "https://allowed-cors-domain.example"