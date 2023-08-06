# Copyright (C) 2022 Cochise Ruhulessin <cochiseruhulessin@gmail.com>
# 
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
"""Declares :class:`GoogleEndpoint`."""
import fastapi
import fastapi.params
import httpx
from ckms.jose import PayloadCodec
from ckms.types import JSONWebToken
from ckms.types import MalformedPayload
from ckms.types import ServerMetadata
from fastapi.security.utils import get_authorization_scheme_param

from cbra import Endpoint
from cbra.cors import NullCorsPolicy
from cbra.exceptions import AuthenticationRequired
from cbra.exceptions import Forbidden
from cbra.exceptions import InvalidAuthorizationScheme
from cbra.exceptions import UntrustedIssuer
from cbra.params import CurrentServer
from cbra.types import ICorsPolicy
from cbra.types import IPrincipal
from .const import GOOGLE_OPENID_SERVER
from .serviceaccountprincipal import ServiceAccountPrincipal


class GoogleEndpoint(Endpoint):
    """A :class:`cbra.Endpoint` implementation that is invoked by Google
    services, such as Cloud Scheduler or Pub/Sub.
    """
    __module__: str = 'cbra.ext.google'
    cors_policy: type[ICorsPolicy] = NullCorsPolicy
    method: str = "POST"
    principal: ServiceAccountPrincipal
    require_authentication: bool = True

    #: The codec configured with the Google JWKS used to verify the
    #: JWT.
    codec: PayloadCodec | None = None

    #: The set of subjects that are accepted by this endpoint.
    service_accounts: set[str] | None = None

    @classmethod
    async def principal_factory(
        cls,
        request: fastapi.Request,
        audience: str = CurrentServer,
        authorization: str | None = fastapi.Header(
            alias='Authorization',
            default=None,
            title="Authorization",
            description=(
                "The `Authorization` header must specify the `Bearer` scheme, "
                "holding a JWT that was signed by Google. The `iss` claim must "
                "be `https://accounts.google.com` and the signing keys to "
                "verify the signature are discovered using the OAuth 2.x/"
                "OpenID Connect metadata protocol. Any failure in fetching "
                "the JWKS, signature validation or JWT claims deserialization "
                "results in a `403` error response. If the `Authorization` "
                "header is missing, then this endpoint responds with a "
                "`401` status."
            )
        )
    ) -> IPrincipal | None:
        """Parse the ``Authorization`` header and verify that the bearer token
        was issued by Google and signed with the proper keys. Return the a new
        :class:`GooglePrincipal` instance.

        Args:
            authorization (str): the `Authorization` header specified on the
                HTTP request that is being authenticated.

        Returns:
            :class:`~cbra.ext.google.GooglePrincipal`

        Raises:
            :class:`~cbra.exceptions.AuthenticationRequired`: the `Authorization`
                header was not provided by the HTTP request and the endpoint class
                set the :attr:`require_authentication` to ``True``.
            :class:`~cbra.exceptions.InvalidAuthorizationScheme`: the `Authorization`
                header was present, but the scheme was invalid i.e. not `Bearer`.
            :class:`~cbra.exceptions.UntrustedIssuer`: the JWT was not issued
                by Google.
            :class:`~ckms.jose.Unusable`: the JWT payload could not be decoded,
                most probably because it was encrypted with a key that is not
                in the possession of the server.
            :class:`~ckms.jose.JOSEException`: any other issues with the JWT
                that were not listed above. Inspect the :attr:`JOSEException.code`
                attribute to determine the cause.
        """
        # If the token was not provided, then return None or raise an
        # error if authentication is required.
        if not authorization:
            if cls.require_authentication:
                raise AuthenticationRequired
            return None
    
        scheme, token = get_authorization_scheme_param(authorization or '')
        if str.lower(scheme or '') != 'bearer':
            raise InvalidAuthorizationScheme

        # Fetch the Google keys if they are not known yet, and verify the
        # signature
        if GoogleEndpoint.codec is None:
            async with httpx.AsyncClient() as client:
                metadata = await ServerMetadata.discover(
                    client=client,
                    issuer=GOOGLE_OPENID_SERVER
                )
                GoogleEndpoint.codec = PayloadCodec(
                    verifier=await metadata.get_jwks(client=client)
                )
        _, claims = await GoogleEndpoint.codec.jwt(token)
        if not isinstance(claims, JSONWebToken): # type: ignore
            raise MalformedPayload(http_status_code=403)
        assert claims.iss is not None # nosec
        if claims.iss != GOOGLE_OPENID_SERVER: # pragma: no cover
            # This should never happen, but check just to be sure.
            raise UntrustedIssuer(claims.iss)
        claims.verify(
            audience={
                audience,
                f'{request.url.scheme}://{request.url.netloc}{request.url.path}'
            },
            required={'iss', 'aud', 'sub', 'exp', 'email'}
        )
        assert claims.sub is not None # nosec
        assert claims.extra.get('email') is not None # nosec
        if cls.service_accounts is not None\
        and claims.extra['email'] not in cls.service_accounts:
            raise Forbidden(
                message=(
                    f"The service account or user {claims.extra['email']} is not "
                    "allowed to invoke this endpoint."
                )
            )
        return ServiceAccountPrincipal(
            email=claims.extra['email'],
            sub=str(claims.sub)
        )

    @Endpoint.register_exception # type: ignore
    async def on_uncaught_exception(
        self,
        exception: Exception
    ) -> fastapi.Response:
        """Ensures that the exception is suppresssed."""
        if not isinstance(self.transaction, fastapi.params.Depends):
            self.transaction.abort()
        self.logger.exception(
            "Caught fatal %s while handling message.",
            type(exception).__name__
        )
        return fastapi.Response(
            status_code=200,
            headers={'X-Error-Code': "UNCAUGHT_EXCEPTION"}
        )