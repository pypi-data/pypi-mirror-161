"""Declares :class:`ClientCredentialsGrant`"""
import typing

import pydantic

from .basegrant import BaseGrant
from .granttype import GrantType
from .spaceseparatedlist import SpaceSeparatedList


class ClientCredentialsGrant(BaseGrant):
    __module__: str = 'cbra.ext.oauth2.types'

    grant_type: typing.Literal[GrantType.client_credentials] = pydantic.Field(
        default=...,
        title="Grant type",
        description=(
            "Must be `client_credentials`."
        ),
        example="client_credentials"
    )

    scope: SpaceSeparatedList | None = pydantic.Field(
        default=[],
        title="Scope",
        description=(
            "The requested scope that the client wants to obtain an access "
            "token for."
        )
    )