# pylint: skip-file
import urllib.parse

import httpx

from .iauthorizationcodeflow import IAuthorizationCodeFlow
from .test_unit_jar import TestJARFlow as Base


class TestRequestParameter(Base):

    async def create_authorize_response(
        self,
        client: httpx.AsyncClient,
        params: dict[str, str],
        status_code: int = 303,
        error: str | None = None,
        headers: dict[str, str] | None = None
    ) -> tuple[urllib.parse.ParseResult, dict[str, str], dict[str, str]]:
        params = {
            'client_id': self.client_id,
            'request': (
                await self.create_jar(
                    codec=await self.get_client_codec(
                        keychain=await self.get_client_keychain(self.client_key)
                    ),
                    params=params
                )
            )
        }
        return await IAuthorizationCodeFlow.create_authorize_response(
            self,
            client=client,
            params=params,
            status_code=status_code,
            error=error
        )


class TestRequestParameterCORS(TestRequestParameter):
    origin = "https://allowed-cors-domain.example"