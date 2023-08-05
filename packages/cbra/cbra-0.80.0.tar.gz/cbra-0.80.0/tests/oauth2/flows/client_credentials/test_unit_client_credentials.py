# pylint: skip-file
import httpx
import pytest
import pytest_asyncio
from ckms.core import Keychain

from cbra.ext.oauth2.types import ClientAssertionType
from cbra.ext.oauth2.types import IClient
from cbra.ext.oauth2.types import GrantType
from ...assertedclientmixin import AssertedClientMixin
from ...servertest import ServerTest


class TestClientCredentialsFlow(ServerTest, AssertedClientMixin):
    base_url: str = "https://cbra-oauth2.localhost"
    client_id: str = 'test-client-credentials'
    client_key: str = "confidential1"
    redirect_uri: str = "https://localhost:8000/callback"
    assertion_type: ClientAssertionType = ClientAssertionType.jwt_bearer

    @pytest_asyncio.fixture # type: ignore
    async def rejected_keychain(self) -> Keychain:
        keychain = Keychain()
        keychain.configure({
            'sig': {
                'provider': "local",
                'kty': "OKP",
                'path': "pki/confidential2.key",
                'alg': "EdDSA",
                'crv': "Ed448",
                'use': 'sig'
            }
        })
        await keychain
        return keychain

    @pytest.mark.asyncio
    async def test_assertion_obtain_token(
        self,
        client_keychain: Keychain,
        client: httpx.AsyncClient
    ):
        assertion = await self.get_client_assertion(
            keychain=client_keychain,
            iss=self.client_id,
            aud=self.token_url,
            sub=self.client_id
        )
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'client_assertion_type': self.assertion_type,
                'client_assertion': assertion,
                'scope': "system"
            }
        )
        dto = response.json()
        assert response.status_code == 200, response.text
        self.assert_rfc9068(dto['access_token'], 'iss', self.base_url)
        self.assert_rfc9068(dto['access_token'], 'sub', self.client_id)
        self.assert_rfc9068(dto['access_token'], 'client_id', self.client_id)
        self.assert_rfc9068(dto['access_token'], 'scope', "system")


    # If the request does not include a "resource" parameter, the authorization
    # server MUST use a default resource indicator in the "aud" claim (RFC 9068,
    # Section 3).
    @pytest.mark.asyncio
    async def test_assertion_sets_default_resource(
        self,
        client_keychain: Keychain,
        client: httpx.AsyncClient
    ):
        assertion = await self.get_client_assertion(
            keychain=client_keychain,
            iss=self.client_id,
            aud=self.token_url,
            sub=self.client_id
        )
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'client_assertion_type': self.assertion_type,
                'client_assertion': assertion,
                'scope': "system"
            }
        )
        dto = response.json()
        assert response.status_code == 200, response.text
        self.assert_rfc9068(dto['access_token'], 'aud', {self.base_url})

    @pytest.mark.asyncio
    async def test_assertion_sets_allowed_resource(
        self,
        client_keychain: Keychain,
        client: httpx.AsyncClient
    ):
        assertion = await self.get_client_assertion(
            keychain=client_keychain,
            iss=self.client_id,
            aud=self.token_url,
            sub=self.client_id
        )
        resource = "https://resource1.unimatrixapis.localhost"
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'client_assertion_type': self.assertion_type,
                'client_assertion': assertion,
                'scope': "system",
                'resource': [resource]
            }
        )
        dto = response.json()
        assert response.status_code == 200, response.text
        self.assert_rfc9068(dto['access_token'], 'aud', {resource})

    @pytest.mark.asyncio
    async def test_assertion_sets_allowed_resources(
        self,
        client_keychain: Keychain,
        client: httpx.AsyncClient,
        current_client: IClient
    ):
        current_client.allow_multiple_audiences = True
        assertion = await self.get_client_assertion(
            keychain=client_keychain,
            iss=self.client_id,
            aud=self.token_url,
            sub=self.client_id
        )
        resources = [
            "https://resource1.unimatrixapis.localhost",
            "https://resource2.unimatrixapis.localhost"
        ]
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'client_assertion_type': self.assertion_type,
                'client_assertion': assertion,
                'scope': "system",
                'resource': resources
            }
        )
        current_client.allow_multiple_audiences = False
        dto = response.json()
        assert response.status_code == 200, response.text
        self.assert_rfc9068(dto['access_token'], 'aud', set(resources))

    @pytest.mark.asyncio
    async def test_assertion_forbids_multiple_resources(
        self,
        client_keychain: Keychain,
        client: httpx.AsyncClient
    ):
        assertion = await self.get_client_assertion(
            keychain=client_keychain,
            iss=self.client_id,
            aud=self.token_url,
            sub=self.client_id
        )
        resources = [
            "https://resource1.unimatrixapis.localhost",
            "https://resource2.unimatrixapis.localhost"
        ]
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'client_assertion_type': self.assertion_type,
                'client_assertion': assertion,
                'scope': "system",
                'resource': resources
            }
        )
        assert response.status_code == 400, response.text
        self.assert_error(response, 'invalid_grant')

    @pytest.mark.asyncio
    async def test_assertion_forbided_non_whitelisted_resources(
        self,
        client_keychain: Keychain,
        client: httpx.AsyncClient
    ):
        assertion = await self.get_client_assertion(
            keychain=client_keychain,
            iss=self.client_id,
            aud=self.token_url,
            sub=self.client_id
        )
        resource = "https://resource3.unimatrixapis.localhost"
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'client_assertion_type': self.assertion_type,
                'client_assertion': assertion,
                'scope': "system",
                'resource': resource
            }
        )
        assert response.status_code == 400, response.text
        self.assert_error(response, 'invalid_grant')

    @pytest.mark.asyncio
    async def test_assertion_can_not_use_multiple_times(
        self,
        client_keychain: Keychain,
        client: httpx.AsyncClient
    ):
        assertion = await self.get_client_assertion(
            keychain=client_keychain,
            iss=self.client_id,
            aud=self.token_url,
            sub=self.client_id
        )
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'client_assertion_type': self.assertion_type,
                'client_assertion': assertion,
                'scope': "system"
            }
        )
        assert response.status_code == 200, response.text
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'client_assertion_type': self.assertion_type,
                'client_assertion': assertion,
                'scope': "system"
            }
        )
        assert response.status_code == 400, response.text
        self.assert_error(response, 'invalid_client')

    @pytest.mark.asyncio
    async def test_assertion_audience_must_be_token_endpoint(
        self,
        client_keychain: Keychain,
        client: httpx.AsyncClient
    ):
        assertion = await self.get_client_assertion(
            keychain=client_keychain,
            iss=self.client_id,
            aud=self.base_url,
            sub=self.client_id
        )
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'client_assertion_type': self.assertion_type,
                'client_assertion': assertion,
                'scope': "system"
            }
        )
        assert response.status_code == 400, response.text
        self.assert_error(response, "invalid_grant")

    @pytest.mark.asyncio
    async def test_assertion_signature_must_be_from_client(
        self,
        rejected_keychain: Keychain,
        client: httpx.AsyncClient
    ):
        assertion = await self.get_client_assertion(
            keychain=rejected_keychain,
            iss=self.client_id,
            aud=self.token_url,
            sub=self.client_id
        )
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'client_assertion_type': self.assertion_type,
                'client_assertion': assertion,
                'scope': "system"
            }
        )
        assert response.status_code == 400, response.text
        self.assert_error(response, "invalid_grant")

    # If the client JWT is not valid, the authorization server constructs
    # an error response as defined in OAuth 2.0 [RFC6749].  The value of
    # the "error" parameter MUST be the "invalid_client" error code.
    # The authorization server MAY include additional information regarding
    # the reasons the JWT was considered invalid using the "error_description"
    # or "error_uri" parameters.
    @pytest.mark.asyncio
    async def test_assertion_sub_must_match_client(
        self,
        client_keychain: Keychain,
        client: httpx.AsyncClient
    ):
        assertion = await self.get_client_assertion(
            keychain=client_keychain,
            iss=self.client_id,
            aud=self.token_url,
            sub='adifferentclient'
        )
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'client_assertion_type': self.assertion_type,
                'client_assertion': assertion,
                'scope': "system"
            }
        )
        assert response.status_code == 400, response.text
        self.assert_error(response, "invalid_client")

    @pytest.mark.asyncio
    async def test_assertion_iss_must_match_client(
        self,
        client_keychain: Keychain,
        client: httpx.AsyncClient
    ):
        assertion = await self.get_client_assertion(
            keychain=client_keychain,
            iss='adifferentclient',
            aud=self.token_url,
            sub=self.client_id
        )
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'client_assertion_type': self.assertion_type,
                'client_assertion': assertion,
                'scope': "system"
            }
        )
        assert response.status_code == 400, response.text
        self.assert_error(response, "invalid_client")

    # The client MUST authenticate with the authorization server (RFC 6749, 4.4.2)
    @pytest.mark.asyncio
    async def test_client_must_authenticate(
        self,
        client: httpx.AsyncClient
    ):
        response = await client.post( # type: ignore
            url=self.token_url,
            json={
                'grant_type': GrantType.client_credentials,
                'client_id': self.client_id,
                'scope': "system"
            }
        )
        self.assert_error(response, "invalid_client")