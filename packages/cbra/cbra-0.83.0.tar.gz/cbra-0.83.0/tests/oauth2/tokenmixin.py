# pylint: skip-file
# type: ignore
import datetime
import secrets
import typing

import pytest
import pytest_asyncio
from ckms.jose import PayloadCodec
from ckms.types import JSONWebToken
from ckms.types import JSONWebKey
from httpx import AsyncClient

from cbra.ext.oauth2.types import GrantType
from cbra.ext.oauth2.types import ISubject
from cbra.utils import current_timestamp
from .conftest import get_subject_codec

class TokenMixin:
    base_url: str = "https://cbra-oauth2.localhost"
    default_scope: typing.Set[str] = {"read"}

    @pytest.fixture
    def token_audience(self) -> str:
        return f'{self.base_url}/oauth2/token'

    async def get_jwt_grant(self, subject: ISubject, **claims: typing.Any) -> str:
        codec = await get_subject_codec(subject)
        return await self.sign_jwt(codec, **claims)

    @pytest_asyncio.fixture # type: ignore
    async def grant(self, current_subject: ISubject, token_audience: str):
        return await self.get_jwt_grant(
            subject=current_subject,
            iss=current_subject.sub,
            aud=token_audience,
            sub=current_subject.sub
        )

    @pytest.fixture
    def scope(self) -> typing.Set[str]:
        return self.default_scope

    @pytest_asyncio.fixture # type: ignore
    async def token(
        self,
        client: AsyncClient,
        grant: str,
        current_subject: ISubject,
        scope: typing.Set[str]
    ):
        current_subject.client_scope['jwt'] = scope
        request = dict(
            client_id='jwt',
            grant_type=GrantType.jwt_bearer,
            assertion=grant
        )
        if scope:
            request['scope'] = str.join(' ', sorted(scope))
        response = await client.post(url='/oauth2/token', json=request)
        assert response.status_code == 200, response.text
        dto = response.json()
        return dto['access_token']

    async def sign_jwt(
        self,
        codec: PayloadCodec,
        **claims: typing.Any
    ) -> str:
        now = current_timestamp()
        defaults = {
            'jti': secrets.token_urlsafe(24),
            'iat': now,
            'exp': now+600,
            'nbf': now
        }
        defaults.update(claims)
        return await codec.encode(
            JSONWebToken(**defaults),
            signers=['sig']
        )