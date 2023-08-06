"""Declares :class:`IssuerJWKS`."""
import urllib.parse

import httpx
import pydantic
from ckms.types import JSONWebKeySet

from cbra.exceptions import MisbehavingIssuer
from cbra.exceptions import UnreachableIssuer
from cbra.exceptions import UntrustedIssuer


class IssuerJWKS:
    """Maintains the keys for a remote issuer."""
    __module__: str = 'cbra.ext.jwks'
    keysets: dict[str, JSONWebKeySet]
    IssuerDoesNotExist: type[UntrustedIssuer] = UntrustedIssuer

    def __init__(self):
        self.keysets = {}

    async def get(
        self,
        issuer: str,
        trusted: set[str]
    ) -> JSONWebKeySet:
        if issuer not in self.keysets and issuer not in trusted:
            raise self.IssuerDoesNotExist(issuer)
        if issuer not in self.keysets:
            self.keysets[issuer] = await self.discover(issuer)
        return self.keysets[issuer]

    async def discover(self, issuer: str) -> JSONWebKeySet:
        """Discover the issuer's JSON Web Key Set (JWKS) using the
        OAuth 2.0/OpenID Connect server metadata.
        """
        p = urllib.parse.urlparse(issuer)
        base_url = f"{p.scheme or 'https'}://{p.netloc}"
        async with httpx.AsyncClient(base_url=base_url) as client:
            jwks_uri = None
            for path in [
                '/.well-known/openid-configuration',
                '/.well-known/oauth-authorization-server'
            ]:
                response = await self._get(
                    client=client,
                    issuer=issuer,
                    url=path
                )
                if response.status_code != 200:
                    continue
                metadata = response.json()
                jwks_uri = metadata.get('jwks_uri')
            if jwks_uri is None:
                raise MisbehavingIssuer(
                    detail=(
                        "The OAuth 2.0/OpenID Connect metadata could not be "
                        "retrieve from well-known URIs."
                    )
                )
            response = await self._get(
                client=client,
                issuer=issuer,
                url=jwks_uri
            )
            if response.status_code >= 400:
                raise MisbehavingIssuer(
                    detail="The `jwks_uri` returned a non-200 response."
                )
            try:
                jwks = JSONWebKeySet(**response.json())
            except (pydantic.ValidationError, TypeError, ValueError):
                raise MisbehavingIssuer(
                    detail=(
                        "The `jwks_uri` did not serve a JSON Web Key Set "
                        "(JWKS) or it could not be deserialized."
                    )
                )

        return jwks

    async def _get(
        self,
        client: httpx.AsyncClient,
        issuer: str,
        url: str
    ) -> httpx.Response:
        try:
            return await client.get(url) # type: ignore
        except httpx.RequestError:
            raise UnreachableIssuer