"""Declares :class:`FormParser`."""
import typing

import fastapi
from ckms.jose import PayloadCodec
from ckms.types import Malformed
from unimatrix.exceptions import CanonicalException

from cbra.types import IParser
from ..exceptions import Error
from ..exceptions import NoSuchClient
from ..types import IClientRepository


class JARParser(IParser):
    """Parser for JWT-Secured Authorization Requests."""
    __module__: str = 'cbra.ext.oauth2.parsers'
    media_type: str = 'application/oauth-authz-req+jwt'
    token_type: str = "oauth-authz-req+jwt"
    charset: str = "utf-8"
    clients: IClientRepository
    issuer: str
    server_codec: PayloadCodec
    max_age: int = 180

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

    async def parse(self,
        request: fastapi.Request,
        media_type: str | None = None,
        parser_context: dict[str, typing.Any] | None = None
    ) -> dict[str, typing.Any]:
        """Parses the incoming bytestream as a JWT-Secured Authorization Request
        (JAR).
        """
        try:
            jws, claims = await self.server_codec.jwt(
                token=await request.body(),
                accept=self.token_type
            )
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