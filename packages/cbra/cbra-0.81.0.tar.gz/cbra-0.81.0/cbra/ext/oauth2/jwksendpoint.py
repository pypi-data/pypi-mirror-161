"""Declares :class:`JWKSEndpoint`."""
import typing

from ckms.types import JSONWebKeySet

from .endpoint import Endpoint
from .params import ServerJWKS


class JWKSEndpoint(Endpoint):
    """Single-tenant endpoint exposing the public keys used by the server to
    verify signatures and encrypt data, as a JSON Web Key Set (JWKS).
    """
    __module__: str = 'cbra.ext.oauth2'
    description: str = (
        "The **JWKS Endpoint** returns a JSON object containing the "
        "public keys that clients may use to encrypt data it sends "
        "to the authorization server, and to verify signatures created "
        "by the authorization server."
    )
    disable_options: bool = True
    methods: set[str] = {'GET'}
    options_description: str = (
        "Communicates the allowed methods and CORS options for "
        "the **JWKS Endpoint**."
    )
    summary: str = 'JSON Web Key Set (JWKS)'
    response_model: type[JSONWebKeySet] = JSONWebKeySet
    response_description: str = "The server public keys."

    def __init__(self, jwks: JSONWebKeySet = ServerJWKS):
        self.jwks = jwks

    async def handle(self) -> dict[str, typing.Any]:
        return self.jwks.dict(exclude_defaults=True)