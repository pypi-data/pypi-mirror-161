# pylint: skip-file
import typing

import pytest_asyncio
from ckms.core import Keychain
from ckms.jose import PayloadCodec
from ckms.types import JSONWebToken

from cbra.ext.oauth2 import ConfigFileClientRepository
from cbra.ext.oauth2.types import ClientAssertionType
from cbra.ext.oauth2.types import IClient


class AssertedClientMixin:
    assertion_type: ClientAssertionType = ClientAssertionType.jwt_bearer
    client_id: str
    client_key: str
    token_url: str

    async def get_client_keychain(self, key: typing.Any) -> Keychain:
        raise NotImplementedError

    @pytest_asyncio.fixture # type: ignore
    async def client_keychain(self) -> Keychain:
        return await self.get_client_keychain(self.client_key)

    @pytest_asyncio.fixture # type: ignore
    async def current_client(self) -> IClient:
        return await ConfigFileClientRepository().get(self.client_id)

    async def get_client_assertion(
        self,
        keychain: Keychain,
        **claims: typing.Any
    ) -> str:
        codec = PayloadCodec(signer=keychain)
        claims = {
            'iss': self.client_id,
            'aud': self.token_url,
            'ttl': 30,
            **claims
        }
        return await codec.encode(
            JSONWebToken.strict(**claims),
            signers=['sig']
        )

    @pytest_asyncio.fixture # type: ignore
    async def assertion(
        self,
        client_keychain: Keychain
    ) -> str:
        return await self.get_client_assertion(client_keychain)
