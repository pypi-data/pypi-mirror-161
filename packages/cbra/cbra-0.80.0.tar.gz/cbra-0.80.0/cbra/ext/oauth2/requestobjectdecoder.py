"""Declares :class:`RequestObjectDecoder`."""
from typing import cast
from typing import Any

import fastapi
from ckms.core.models import JSONWebSignature
from ckms.jose import PayloadCodec
from ckms.types import Malformed
from unimatrix.exceptions import CanonicalException

from .exceptions import Error
from .exceptions import NoSuchClient
from .params import ClientRepository
from .params import LocalIssuer
from .params import ServerCodec
from .types import IClientRepository


class RequestObjectDecoder:
    """Decores a **Request Object** as defined in :rfc:`9101`."""
    __module__: str = 'cbra.ext.oauth2'
    clients: IClientRepository
    codec: PayloadCodec
    issuer: str
    token_type: str = "oauth-authz-req+jwt"
    JARNotSigned: type[Error] = type('JARNotSigned', (Error,), {
        'error': 'invalid_request_object',
        'error_description': (
            "A JWT-Secured Authorization Request (JAR) must be "
            "signed using a key that is associated to the client."
        )
    })

    TokenTypeError: type[Error] = type('TokenTypeError', (Error,), {
        'error': 'invalid_request_object',
        'error_description': (
            "The JWT-Secured Authorization Request (JAR) was parsed "
            "correctly as a JSON Web Signature (JWS) but the \"typ\" "
            "header claim specified an invalid type. A JWS that "
            "represents a JAR must specify the \"oauth-authz-req+jwt\" "
            "in its header \"typ\" claim."
        )
    })

    InvalidAudience: type[Error] = type('InvalidAudience', (Error,), {
        'error': 'invalid_request_object',
        'error_description': (
            "The audience specified by the JWT-Secured Authorization "
            "Request (JAR) is not accepted by the server."
        )
    })

    InvalidIssuer: type[Error] = type('InvalidIssuer', (Error,), {
        'error': 'invalid_request_object',
        'error_description': (
            "The \"iss\" claim of the JWT-Secured Authorization Request (JAR) "
            "must match the \"client_id\" claim."
        )
    })

    InvalidRequest: type[Error] = type('InvalidRequest', (Error,), {
        'error': 'invalid_request_object',
        'error_description': (
            "The JWT-Secured Authorization Request (JAR) was succesfully "
            "parsed and the signature was valid for the specified client, "
            "but the claims indicate that the token was either not effective, "
            "expired or required claims were missing."
        )
    })

    MalformedRequest: type[Error] = type('MalformedRequest', (Error,), {
        'error': 'invalid_request_object',
        'error_description': (
            "The JWT-Secured Authorization Request (JAR) is malformed and "
            "could not be interpreted by the authorization server."
        )
    })

    InvalidSignature: type[Error] = type('InvalidSignature', (Error,), {
        'error': 'invalid_request_object',
        'error_description': "Signature validation failed."
    })

    def __init__(
        self,
        clients: IClientRepository = ClientRepository,
        codec: PayloadCodec = ServerCodec,
        issuer: str = LocalIssuer
    ) -> None:
        self.clients = clients
        self.codec = codec
        self.issuer = issuer

    async def decode_request(
        self,
        request: fastapi.Request
    ) -> dict[str, Any]:
        """Parses the incoming bytestream as a JWT-Secured Authorization Request
        (JAR).
        """
        return await self.decode_request_object(await request.body())

    async def decode_request_object(
        self,
        obj: bytes | str
    ) -> dict[str, Any]:
        if isinstance(obj, str):
            obj = str.encode(obj, 'ascii')
        try:
            jws, claims = await self.codec.jwt(obj, accept=self.token_type)
        except (Malformed, TypeError, ValueError):
            raise self.MalformedRequest
        if jws.typ != self.token_type:
            raise self.TokenTypeError
        if not bool(jws.signatures): # type: ignore
            raise self.JARNotSigned
        client_id = claims.extra.get('client_id')
        if claims.iss != client_id:
            raise self.InvalidIssuer
        if claims.iss is None or\
        not await self.clients.exists(client_id=claims.iss):
            raise NoSuchClient
        client = await self.clients.get(claims.iss)
        if not await client.verify_jws(jws):
            raise self.InvalidSignature
        try:
            claims.verify(
                audience={self.issuer},
                strict=True
            )
        except CanonicalException as exception:
            if exception.code == "WRONG_AUDIENCE":
                raise self.InvalidAudience
            raise self.InvalidRequest
        return claims.dict()