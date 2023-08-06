# pylint: skip-file
import random
import typing
import urllib.parse

import httpx
import pytest
from ckms.jose import PayloadCodec
from unimatrix.lib.http import parse_qs # type: ignore

import cbra
from cbra.ext.oauth2 import AuthorizationServer
from ...corsmixin import CorsMixin


class IAuthorizationCodeFlow(CorsMixin):
    authorize_url: str
    base_url: str
    client_id: str
    client_key: str
    cors_allowed_origin: str = "https://allowed-cors-domain.example"
    cors_allowed_methods: set[str] = {"GET"}
    origin: str | None = None
    grant_type: str = "authorization_code"
    redirect_uri: str
    redirects: bool = False
    token_url: str
    authorize_status_code: int
    response_type: str

    async def get_token(
        self,
        client: httpx.AsyncClient,
        code: str
    ) -> dict[str, typing.Any]:
        headers = {}
        if self.origin:
            headers['Origin'] = self.origin
            preflight = await client.options( # type: ignore
                url=self.token_url,
                headers={
                    'Origin': self.origin,
                    'Access-Control-Request-Methods': "POST"
                }
            )
            assert preflight.status_code == 200, preflight.status_code
            assert preflight.headers.get('Access-Control-Allow-Origin') == self.origin, preflight.headers
            assert preflight.headers.get('Access-Control-Allow-Credentials') == "false"
            assert "POST" in preflight.headers.get('Access-Control-Allow-Methods', ''), preflight.headers

        response = await client.post( # type: ignore
            url=self.token_url,
            json=await self.get_token_request_params(code),
            headers=headers
        )
        assert response.status_code == 200, response.text
        if self.origin is not None:
            assert 'Access-Control-Allow-Origin' in response.headers, response.headers
            assert response.headers['Access-Control-Allow-Origin'] == self.origin
        return response.json()

    async def get_token_request_params(self, code: str) -> dict[str, typing.Any]:
        return {
            'grant_type': self.grant_type,
            'code': code,
            'redirect_uri': self.redirect_uri,
            **await self.get_token_client_params()
        }

    async def get_token_client_params(self) -> dict[str, typing.Any]:
        return {'client_id': self.client_id}

    async def create_authorize_response(
        self,
        client: httpx.AsyncClient,
        params: dict[str, str],
        status_code: int = 303,
        error: str | None = None,
        headers: dict[str, str] | None = None
    ) -> tuple[urllib.parse.ParseResult, dict[str, str], dict[str, str]]:
        headers = headers or {}
        if self.origin is not None:
            headers['Origin'] = self.origin
        response = await client.get( # type: ignore
            url=self.authorize_url,
            params=params,
            headers=headers,
        )
        if 'Location' not in response.headers:
            dto = response.json()
            assert response.status_code == status_code, f'{response.status_code}: {dto}'
            assert response.headers['Content-Type'] == "application/json"
            assert 'error' in dto
            if error is not None:
                assert dto['error'] == error, dto
            return (urllib.parse.urlparse(''), dict(response.headers), {})
        
        assert response.status_code == status_code, f'{response.status_code}: {response.text}'
        if self.origin is not None:
            assert 'Access-Control-Allow-Origin' in response.headers
            assert response.headers['Access-Control-Allow-Origin'] == self.origin
        p = urllib.parse.urlparse(response.headers['Location'])
        dto = dict(parse_qs(p.query))
        if error is not None:
            assert dto.get('error') == error, dto
        return (
            p,
            dict(response.headers),
            dto
        )

    async def get_minimal_authorize_params(self, **params: typing.Any) -> dict[str, str]:
        return {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            **params
        }

    @pytest.mark.asyncio
    async def test_authorize_with_minimal_parameters(
        self,
        client: httpx.AsyncClient,
        headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        url, headers, result = await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(),
            status_code=303,
            headers=headers
        )
        assert url[:3] == urllib.parse.urlparse(self.redirect_uri)[:3]
        assert 'code' in result, result
        assert 'iss' in result, result
        assert result['iss'] == self.base_url
        token = await self.get_token(
            client=client,
            code=typing.cast(str, result.get('code'))
        )
        assert 'access_token' in token
        assert 'token_type' in token
        assert token['token_type'] == 'Bearer'

        header, claims = PayloadCodec().introspect(token['access_token'])
        assert claims is not None
        assert claims.extra['client_id'] == self.client_id
        assert claims.sub == client.cookies['subject']
        assert header.headers[0].typ == "at+jwt"
        return headers

    @pytest.mark.asyncio
    async def test_authorize_with_minimal_parameters_cors(
        self,
        client: httpx.AsyncClient,
        headers: dict[str, str] | None = None
    ):
        origin = "https://allowed-cors-domain.example"
        await self.test_authorize_with_minimal_parameters(
            client=client,
            headers={
                'Origin': origin
            }
        )

    @pytest.mark.asyncio
    async def test_authorize_with_minimal_parameters_retains_state(
        self,
        client: httpx.AsyncClient
    ) -> None:
        *_, result = await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(
                state='foo'
            ),
            status_code=303
        )
        assert 'state' in result
        assert result.get('state') == 'foo'

    @pytest.mark.asyncio
    async def test_authorize_redirect_error_retains_state(
        self,
        client: httpx.AsyncClient
    ) -> None:
        # Trigger some error that can redirect to the client. Do not run
        # this test on pushed authorization request test cases.
        if not self.redirects or self.origin is not None:
            pytest.skip()
        *_, result = await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(
                state='foo'
            ),
            headers={'Origin': 'https://foo.invalid'},
            error='invalid_origin',
            status_code=303,
        )
        assert 'state' in result
        assert result.get('state') == 'foo'

    @pytest.mark.asyncio
    async def test_authorize_retains_query(
        self,
        client: httpx.AsyncClient
    ) -> None:
        *_, result = await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(
                redirect_uri="https://cbra-oauth2.localhost/callback?foo=bar"
            ),
            status_code=303
        )
        assert 'foo' in result
        assert result.get('foo') == 'bar'

    @pytest.mark.asyncio
    async def test_authorize_unregistered_query_parameter(
        self,
        client: httpx.AsyncClient
    ) -> None:
        await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(
                redirect_uri="https://cbra-oauth2.localhost/callback?bar=foo"
            ),
            status_code=400,
            error="invalid_request"
        )

    @pytest.mark.asyncio
    async def test_authorize_unregistered_query_value(
        self,
        client: httpx.AsyncClient
    ) -> None:
        await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(
                redirect_uri="https://cbra-oauth2.localhost/callback?foo=baz"
            ),
            status_code=400,
            error="invalid_request"
        )

    @pytest.mark.asyncio
    async def test_authorize_rejects_url_with_fragment(
        self,
        client: httpx.AsyncClient
    ) -> None:
        await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(
                redirect_uri=f'{self.redirect_uri}#foo'
            ),
            status_code=400,
            error="invalid_request"
        )

    @pytest.mark.asyncio
    async def test_authorize_rejects_url_not_registered(
        self,
        client: httpx.AsyncClient
    ) -> None:
        await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(
                redirect_uri=f'https://www.example.com'
            ),
            status_code=400,
            error="invalid_request"
        )

    @pytest.mark.asyncio
    async def test_authorize_rejects_non_https(
        self,
        client: httpx.AsyncClient
    ) -> None:
        await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(
                redirect_uri=f'http://cbra-oauth2.localhost/callback'
            ),
            status_code=400,
            error="invalid_request"
        )

    @pytest.mark.asyncio
    async def test_authorize_allows_http_on_loopback(
        self,
        client: httpx.AsyncClient
    ) -> None:
        # Authorization servers MUST require clients to register their complete
        # redirect URI (including the path component) and reject authorization
        # requests that specify a redirect URI that doesn't exactly match the
        # one that was registered; the exception is loopback redirects, where
        # an exact match is required except for the port URI component.
        # (OAuth 2.1 draft, 9.2)
        await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(
                redirect_uri=f"http://127.0.0.1:{random.randint(1000,10000)}"
            ),
            status_code=303
        )

        # The path /callback is not whitelisted in the test client, so
        # this request must fail.
        await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(
                redirect_uri=f"http://127.0.0.1:{random.randint(1000,10000)}/callback"
            ),
            status_code=400,
            error="invalid_request"
        )


    @pytest.mark.asyncio
    async def test_openid_authorize_fails_with_login_required_when_prompt_is_none(
        self,
        client: httpx.AsyncClient
    ) -> None:
        client.cookies.pop('subject', None) # type: ignore
        await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(
                scope="openid",
                prompt="none"
            ),
            status_code=303,
            error="login_required"
        )

    @pytest.mark.asyncio
    async def test_authorize_unauthenticated_redirects_to_login_url(
        self,
        server: AuthorizationServer,
        client: httpx.AsyncClient
    ):
        client.cookies.pop('subject', None) # type: ignore
        server.login_url = "https://www.example.com/login"
        _, headers, query = await self.create_authorize_response(
            client=client,
            params=await self.get_minimal_authorize_params(),
            status_code=303,
        )
        assert 'location' in headers
        assert headers['location'].startswith(server.login_url)
        assert 'next' in query
        assert query['next'].startswith(self.authorize_url)