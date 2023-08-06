"""Declares :class:`JWKSEndpoint`."""
from ckms.types import JSONWebKeySet

import cbra
from cbra.cors import AnonymousReadCorsPolicy
from cbra.cors import CorsPolicyType


class JWKSEndpoint(cbra.Endpoint):
    """Single-tenant endpoint exposing the public keys used by the server to
    verify signatures and encrypt data, as a JSON Web Key Set (JWKS).
    """
    __module__: str = 'cbra.ext.jwks'
    cors_policy: type[CorsPolicyType] = AnonymousReadCorsPolicy
    name: str = 'metadata.jwks'
    description: str = (
        "Provides the JSON Web Key Set (JWKS) that a client may use to "
        "encrypt data (sent to the server) or verify signatures (issued "
        "by the server)."
    )
    method: str = 'GET'
    mount_path: str = '.well-known/jwks.json'
    summary: str = 'JSON Web Key Set (JWKS)'
    response_model: type[JSONWebKeySet] = JSONWebKeySet
    response_model_by_alias: bool = True
    response_description: str = "The server public keys."
    tags: list[str] = ["Server metadata"]
    with_options: bool = True

    async def handle(self) -> JSONWebKeySet:
        return self.request.jwks or JSONWebKeySet()
