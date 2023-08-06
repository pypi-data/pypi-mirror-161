# pylint: skip-file
# type: ignore
import secrets

import pytest
from ckms.jose import PayloadCodec
from httpx import AsyncClient

from cbra.ext.oauth2 import ClientConfig
from cbra.ext.oauth2.types import GrantType
from cbra.ext.oauth2.types import ISubject
from cbra.ext.oauth2.types import TokenRequestParameters
from ...conftest import get_subject_codec
from ...servertest import ServerTest
from ...tokenmixin import TokenMixin


class TestJWTBearerAssertion(ServerTest, TokenMixin):

    async def get_token_request(self, **kwargs: str):
        defaults = {}
        defaults.update(**kwargs)
        return defaults

    def get_clients_available(self):
        return {
            'jwt': ClientConfig(
                client_id='jwt',
                grant_types_supported=[
                    GrantType.jwt_bearer.value
                ]
            )
        }

    @pytest.mark.asyncio
    async def test_token_endpoint(self, client: AsyncClient, grant: str):
        request = TokenRequestParameters.parse_obj({
            'client_id': 'jwt',
            'grant_type': GrantType.jwt_bearer,
            'assertion': grant
        })
        response = await client.post(
            url='/oauth2/token',
            content=request.json(),
            headers={'Content-Type': "application/json"}
        )
        assert response.status_code == 200, response.text

    @pytest.mark.asyncio
    async def test_token_endpoint_with_disabled_scope(self, client: AsyncClient, grant: str):
        request = TokenRequestParameters.parse_obj({
            'client_id': 'jwt',
            'grant_type': GrantType.jwt_bearer,
            'assertion': grant,
            'scope': "openid profile foo"
        })
        response = await client.post(
            url='/oauth2/token',
            content=request.json(),
            headers={'Content-Type': "application/json"}
        )
        self.assert_error(response, "invalid_scope")

    @pytest.mark.asyncio
    async def test_token_endpoint_with_non_consented_scope(self, client: AsyncClient, grant: str):
        request = TokenRequestParameters.parse_obj({
            'client_id': 'jwt',
            'grant_type': GrantType.jwt_bearer,
            'assertion': grant,
            'scope': "openid profile email"
        })
        response = await client.post(
            url='/oauth2/token',
            content=request.json(),
            headers={'Content-Type': "application/json"}
        )
        self.assert_error(response, "invalid_scope")

    @pytest.mark.asyncio
    async def test_cannot_replay_token(self, client: AsyncClient, grant: str):
        request = TokenRequestParameters.parse_obj({
            'client_id': 'jwt',
            'grant_type': GrantType.jwt_bearer,
            'assertion': grant
        })
        response = await client.post(
            url='/oauth2/token',
            content=request.json(),
            headers={'Content-Type': "application/json"}
        )
        assert response.status_code == 200, response.text
        response = await client.post(
            url='/oauth2/token',
            content=request.json(),
            headers={'Content-Type': "application/json"}
        )
        assert response.status_code == 400, response.text

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        response = await client.get('/rfc9068')
        assert response.status_code == 401, response.text

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_valid_token(self, client: AsyncClient, token: str):
        response = await client.get(
            url='/rfc9068',
            headers={
                'Authorization': f"Bearer {token}"
            }
        )
        assert response.status_code == 200, response.text


    @pytest.mark.asyncio
    async def test_protected_endpoint_with_invalid_scheme(self, client: AsyncClient, token: str):
        response = await client.get(
            url='/rfc9068',
            headers={
                'Authorization': f"Foo {token}"
            }
        )
        assert response.status_code == 403, response.text

    @pytest.mark.asyncio
    async def test_token_endpoint_returns_invalid_client_on_non_existing(
        self,
        client: AsyncClient,
        grant: str
    ):
        request = dict(
            client_id=secrets.token_hex(2),
            grant_type=GrantType.jwt_bearer,
            assertion=grant
        )
        response = await client.post(url='/oauth2/token', json=request)
        self.assert_error(response, 'invalid_client')

    @pytest.mark.asyncio
    async def test_token_endpoint_returns_invalid_client_on_missing(
        self,
        client: AsyncClient,
        grant: str
    ):
        request = dict(
            grant_type=GrantType.jwt_bearer,
            assertion=grant
        )
        response = await client.post(url='/oauth2/token', json=request)
        self.assert_error(response, 'invalid_client')

    @pytest.mark.asyncio
    async def test_token_endpoint_rejects_assertion_with_signature_from_mismatching_issuer(
        self,
        client: AsyncClient,
        codec: PayloadCodec,
        current_subject: ISubject,
        alice: ISubject
    ):
        assert alice.sub != current_subject.sub
        # HACK
        await get_subject_codec(alice)
        grant = await self.sign_jwt(
            codec,
            iss=alice.sub,
            aud=f'{self.base_url}/oauth2/token',
            sub=alice.sub,
        )
        request = dict(
            client_id="jwt",
            grant_type=GrantType.jwt_bearer,
            assertion=grant
        )
        response = await client.post(url='/oauth2/token', json=request)
        self.assert_error(response, 'invalid_grant')

    @pytest.mark.asyncio
    async def test_token_endpoint_rejects_assertion_from_unknown_subject(
        self,
        client: AsyncClient,
        current_subject: ISubject,
        trudy: ISubject
    ):
        assert trudy.sub != current_subject.sub
        # HACK
        codec = await get_subject_codec(trudy)
        grant = await self.sign_jwt(
            codec,
            iss=trudy.sub,
            aud=f'{self.base_url}/oauth2/token',
            sub=trudy.sub,
        )
        request = dict(
            client_id="jwt",
            grant_type=GrantType.jwt_bearer,
            assertion=grant
        )
        response = await client.post(url='/oauth2/token', json=request)
        self.assert_error(response, 'invalid_request')

    @pytest.mark.asyncio
    async def test_token_endpoint_rejects_escalated_scoped(
        self,
        client: AsyncClient,
        grant: str
    ):
        request = dict(
            client_id="jwt",
            grant_type=GrantType.jwt_bearer,
            assertion=grant,
            scope=[secrets.token_hex(4)]
        )
        response = await client.post(url='/oauth2/token', json=request)
        self.assert_error(response, 'invalid_scope')

    @pytest.mark.asyncio
    async def test_token_endpoint_rejects_audience_other_than_itself(
        self,
        client: AsyncClient,
        codec: PayloadCodec,
        current_subject: ISubject,
    ):
        grant = await self.sign_jwt(
            codec,
            iss=current_subject.sub,
            aud=f'{self.base_url}',
            sub=current_subject.sub,
        )
        request = dict(
            client_id="jwt",
            grant_type=GrantType.jwt_bearer,
            assertion=grant,
            scope=[secrets.token_hex(4)]
        )
        response = await client.post(url='/oauth2/token', json=request)
        self.assert_error(response, 'invalid_grant')

    @pytest.mark.asyncio
    async def test_token_endpoint_rejects_token_audiences_that_is_not_approved(
        self,
        client: AsyncClient,
        grant: str
    ):
        request = dict(
            client_id="jwt",
            grant_type=GrantType.jwt_bearer,
            assertion=grant,
            resource="foo"
        )
        response = await client.post(url='/oauth2/token', json=request)
        self.assert_error(response, 'invalid_grant')

    @pytest.mark.asyncio
    async def test_malformed_returns_invalid_grant(self, client: AsyncClient, grant: str):
        header, payload, signature = str.split(grant, '.')
        request = TokenRequestParameters.parse_obj({
            'client_id': 'jwt',
            'grant_type': GrantType.jwt_bearer,
            'assertion': 'foo'
        })
        response = await client.post(
            url='/oauth2/token',
            content=request.json(),
            headers={'Content-Type': "application/json"}
        )
        self.assert_error(response, "invalid_grant")

    @pytest.mark.asyncio
    async def test_malformed_header_returns_invalid_grant(self, client: AsyncClient, grant: str):
        header, payload, signature = str.split(grant, '.')
        request = TokenRequestParameters.parse_obj({
            'client_id': 'jwt',
            'grant_type': GrantType.jwt_bearer,
            'assertion': str.join('.', ['foo', payload, signature])
        })
        response = await client.post(
            url='/oauth2/token',
            content=request.json(),
            headers={'Content-Type': "application/json"}
        )
        self.assert_error(response, "invalid_grant")

    @pytest.mark.asyncio
    async def test_malformed_payload_returns_invalid_grant(self, client: AsyncClient, grant: str):
        header, payload, signature = str.split(grant, '.')
        request = TokenRequestParameters.parse_obj({
            'client_id': 'jwt',
            'grant_type': GrantType.jwt_bearer,
            'assertion': str.join('.', [header, 'foo', signature])
        })
        response = await client.post(
            url='/oauth2/token',
            content=request.json(),
            headers={'Content-Type': "application/json"}
        )
        self.assert_error(response, "invalid_grant")

    @pytest.mark.asyncio
    async def test_malformed_signature_returns_invalid_grant(self, client: AsyncClient, grant: str):
        header, payload, signature = str.split(grant, '.')
        request = TokenRequestParameters.parse_obj({
            'client_id': 'jwt',
            'grant_type': GrantType.jwt_bearer,
            'assertion': str.join('.', [header, payload, 'foo'])
        })
        response = await client.post(
            url='/oauth2/token',
            content=request.json(),
            headers={'Content-Type': "application/json"}
        )
        self.assert_error(response, "invalid_grant")