"""Declares :class:`TokenExchangeRequest`."""
import enum
from pydoc import describe
import typing

import pydantic

from .bodydependantmodel import BodyDependantModel
from .spaceseparatedlist import SpaceSeparatedList
from .tokentype import TokenType


class GrantType(str, enum.Enum):
    token_exchange = 'urn:ietf:params:oauth:grant-type:token-exchange'


class TokenExchangeRequest(BodyDependantModel):
    __module__: str = 'cbra.ext.oauth2'

    grant_type: GrantType = pydantic.Field(
        default=...,
        title="Grant type",
        description=(
            "The value `urn:ietf:params:oauth:grant-type:token- exchange` "
            "indicates that a token exchange is being performed."
        ),
        example="urn:ietf:params:oauth:grant-type:token-exchange",
        enum=[
            "urn:ietf:params:oauth:grant-type:token-exchange"
        ]
    )

    resource: typing.Optional[str] = pydantic.Field(
        default=None,
        title="Resource",
        description=(
            "A URI that indicates the target service or resource where the "
            "client intends to use the requested security token."
        ),
        example="https://oauth2.unimatrixapis.com"
    )

    audience: typing.Optional[str] = pydantic.Field(
        default=None,
        title="Audience",
        description=(
            "The logical name of the target service where the client "
            "intends to use the requested security token.  This serves "
            "a purpose similar to the `resource` parameter but with "
            "the client providing a logical name for the target service."
        ),
        example="oauth2.unimatrixapis.com"
    )

    scope: typing.Optional[SpaceSeparatedList] = pydantic.Field(
        default=[],
        title="Scope",
        description=(
            "A list of space-delimited, case-sensitive strings, hat allow "
            "the client to specify the desired scope of the requested "
            "security token in the context of the service or resource "
            "where the token will be used."
        ),
        example="foo bar baz"
    )

    requested_token_type: TokenType = pydantic.Field(
        default=None,
        title="Requested token type",
        description=(
            "An identifier for the type of the requested security token. "
            "If the requested type is unspecified, the issued token type "
            "is at the discretion of the authorization server and may be "
            "dictated by knowledge of the requirements of the service or "
            "resource indicated by the `resource` or `audience` parameter."
        ),
        example="urn:ietf:params:oauth:token-type:jwt"
    )

    subject_token: str = pydantic.Field(
        default=...,
        title="Subject token",
        description=(
            "A security token that represents the identity of the party "
            "on behalf of whom the request is being made."
        )
    )

    subject_token_type: TokenType = pydantic.Field(
        default=...,
        title="Subject token type",
        description=(
            "An identifier that indicates the type of the security "
            "token in the `subject_token` parameter."
        ),
        example="urn:ietf:params:oauth:token-type:jwt"
    )

    actor_token: str = pydantic.Field(
        default=None,
        title="Actor token",
        description=(
            "A security token that represents the identity of the acting party. "
            "Typically, this will be the party that is authorized to use the "
            "requested security token and act on behalf of the subject."
        )
    )

    actor_token_type: TokenType = pydantic.Field(
        default=None,
        title="Actor token type",
        description=(
            "An identifier that indicates the type of the security "
            "token in the `actor_token` parameter.  This is required "
            "when the `actor_token` parameter is present in the "
            "request but must not be included otherwise."
        ),
        example="urn:ietf:params:oauth:token-type:jwt"
    )