"""Declares :func:`TokenRequestClient`."""
import typing

import fastapi
from ckms.types import ClaimSet
from fastapi.security.utils import get_authorization_scheme_param
from unimatrix.exceptions import CanonicalException

from .exceptions import ClientAuthenticationRequired
from .exceptions import InvalidClient
from .exceptions import InvalidClientAuthenticationScheme
from .exceptions import InvalidGrant
from .exceptions import NoSuchClient
from .types import BaseGrant
from .types import ClientAssertionType
from .types import IClientRepository
from .types import IStorage
from .types import TokenRequestParameters
from .params import ClientRepository
from .params import TokenEndpointURL
from .params import TransientStorage


__all__ = ['TokenRequest']


async def get_token_request(
    request: TokenRequestParameters,
    authorization: typing.Optional[str] = fastapi.Header(
        default=None,
        alias='Authorization',
        description=(
            "The credentials of the client, if the client is confidential "
            "and the credentials are not provided using a client "
            "assertion or the `client_id` and `client_secret` request "
            "parameters."
        )
    ),
    clients: IClientRepository = ClientRepository,
    storage: IStorage = TransientStorage,
    token_endpoint: str = TokenEndpointURL
) -> BaseGrant:
    """Retrieve the current client from either the ``client_id`` specified
    in the request body or the ``Authorization`` header (for confidential
    clients).
    """
    dto = request.get_root()
    client_id = dto.client_id
    grant_type = dto.grant_type

    # Requests to the Token Endpoint always have a client specified. If either
    # the header or the client_id in the request body is missing, we are in an
    # error state.
    if not authorization and not client_id and not dto.has_client_assertion():
        raise InvalidClient(
            error="invalid_client",
            error_description=(
                "Specify the `client_id` parameter in the request body if "
                "the client is public, else provide credentials with the "
                "`Authorization` header."
            )
        )
    if (client_id is not None and not await clients.exists(client_id)):
        raise NoSuchClient

    # If the client attempted to authenticate via the "Authorization" 
    # request header field, the authorization server MUST respond with
    # an HTTP 401 (Unauthorized) status code and include the
    # "WWW-Authenticate" response header field matching the
    # authentication scheme used by the client (RFC 6749, Section 5.2).
    client = None
    scheme, credentials = get_authorization_scheme_param(authorization or '')
    if scheme and credentials:
        if str.lower(scheme) != "bearer":
            raise InvalidClientAuthenticationScheme(
                using=scheme,
                required="Bearer"
            )
        raise NotImplementedError
        # client = await clients.fromcredentials(credentials.credentials)

    # If the client_id variable is None at this point, then it was not provided
    # in the request body, could not be determined from the Authorization header,
    # and there was no client assertion or the client assertion did not verify.
    if client_id is None: # pragma: no cover
        raise NoSuchClient

    # A client MAY use the "client_id" request parameter to identify itself
    # when sending requests to the token endpoint.  In the "authorization_code"
    # "grant_type" request to the token endpoint, an unauthenticated client
    # MUST send its "client_id" to prevent itself from inadvertently accepting
    # a code intended for a client with a different "client_id".  This protects
    # the client from substitution of the authentication code
    # (RFC 6749, Section 3.2.1).
    client = await clients.get(client_id)

    # Authenticate the client using a client assertion, if one was provided.
    if client.is_confidential() and dto.has_client_assertion():
        if dto.client_assertion_type != ClientAssertionType.jwt_bearer:
            raise NotImplementedError
        assert dto.client_assertion is not None # nosec
        try:
            jwt = await client.verify_jwt(
                token=dto.client_assertion,
                decrypter=None,
                audience=token_endpoint
            )
        except (ValueError, TypeError):
            raise InvalidGrant(
                error_description=(
                    "The supplied credential was malformed and could not be "
                    "interpreted by the authorization server."
                )
            )
        except CanonicalException as exception:
            if exception.code in {"INVALID_SIGNATURE", "UNVERIFIABLE"}:
                raise InvalidGrant(
                    error_description=(
                        "The JSON Web Token (JWT) was signed using a key that is "
                        "not accepted by the client."
                    )
                )
            elif exception.code == "WRONG_AUDIENCE":
                raise InvalidGrant(
                    error_description=(
                        "The JSON Web Token (JWT) specified an audience that "
                        "is not accepted by the token endpoint. Ensure that "
                        f"the \"aud\" claim is equal to \"{token_endpoint}\"."
                    )
                )
            raise
        else:
            if jwt.sub != client_id:
                raise InvalidClient(
                    error="invalid_client",
                    error_description=(
                        "The \"sub\" claim in the assertion does not match "
                        "the \"client_id\" specified in the request."
                    )
                )
            elif jwt.iss != client_id:
                raise InvalidClient(
                    error="invalid_client",
                    error_description=(
                        "The \"iss\" claim in the assertion does not match "
                        "the \"client_id\" specified in the request."
                    )
                )
            if await storage.consume(jwt):
                raise InvalidClient(
                    error="invalid_client",
                    error_description=(
                        "A client assertion can only be used once."
                    )
                )

    elif not client.is_public():
        # Other methods are not supported.
        raise ClientAuthenticationRequired

    # Ensure that the client allows the requested grant.
    if not client.allows_grant_type(grant_type):
        raise InvalidGrant(
            error_description=(
                "The client does not allow the given grant: "
                f"{grant_type.value}."
            )
        )

    dto.set_client(client)
    return dto


TokenRequest = fastapi.Depends(get_token_request)