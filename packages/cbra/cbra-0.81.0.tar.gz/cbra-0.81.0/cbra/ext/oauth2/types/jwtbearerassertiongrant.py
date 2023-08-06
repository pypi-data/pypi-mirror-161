"""Declares :class:`JWTBearerAssertionGrant`."""
import typing

import pydantic

from .basegrant import BaseGrant
from .granttype import GrantType
from .spaceseparatedlist import SpaceSeparatedList


class JWTBearerAssertionGrant(BaseGrant):
    __module__: str = 'cbra.ext.oauth2.types'

    grant_type: typing.Literal[GrantType.jwt_bearer] = pydantic.Field(
        default=...,
        title="Grant type",
        description=(
            "Must be `urn:ietf:params:oauth:grant-type:jwt-bearer`."
        ),
        example="urn:ietf:params:oauth:grant-type:jwt-bearer"
    )

    scope: SpaceSeparatedList | None = pydantic.Field(
        default=[],
        title="Scope",
        description=(
            "The requested scope that was previously granted to the subject "
            "or client."
        )
    )

    assertion: str = pydantic.Field(
        default=None,
        title="Assertion",
        description=(
            "The digitally signed document asserting the identity of the "
            "subject.\n\n"
            f"For grants of type `{GrantType.jwt_bearer.value}`, "
            "the `assertion` parameter contains a single JWT. The claims "
            "`exp`, `iat`, `nbf` must be present, in addition to the following"
            " claims:"
            "\n- `iss` - the OAuth 2.0 client id if the assertion is self-issued, "
            "otherwise the identifier of the third-party issuer."
            "\n- `aud` - the URL of the token endpoint."
            "\n- `sub` - identifies the subject on behalf of whom the access token "
            "is requested, i.e. the resource owner."
            "\n- `jti` - a randomly generated identifier for this specific assertion."
        )
    )