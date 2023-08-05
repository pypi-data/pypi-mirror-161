"""Declares :class:`AuthorizationCodeGrant`."""
import typing

import pydantic

from .basegrant import BaseGrant
from .granttype import GrantType


class AuthorizationCodeGrant(BaseGrant):
    __module__: str = 'cbra.ext.oauth2.types'

    grant_type: typing.Literal[GrantType.authorization_code] = pydantic.Field(
        default=...,
        title="Grant type",
        description=(
            "Must be `authorization_code`."
        ),
        example="authorization_code"
    )

    code: str = pydantic.Field(
        default=...,
        title="Authorization code",
        description=(
            "The authorization code that was received from the authorization "
            "server through user-agent redirection."
        )
    )

    redirect_uri: str = pydantic.Field(
        default=None,
        title="Redirect URI",
        description=(
            "Required if the `redirect_uri` parameter was included in the "
            "authorization request and their values must be identical, else "
            "this parameter must be absent from the request."
        )
    )