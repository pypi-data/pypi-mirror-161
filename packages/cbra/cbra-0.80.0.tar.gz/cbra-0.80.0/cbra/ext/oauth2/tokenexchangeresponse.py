"""Declares :class:`TokenExchangeResponse`"""
import typing

import pydantic

from .tokentype import TokenType


class TokenExchangeResponse(pydantic.BaseModel):
    __module__: str = 'cbra.ext.oauth2'

    access_token: str = pydantic.Field(
        default=...,
        description=(
            "The security token issued by the authorization server "
            "in response to the token exchange request."
        )
    )

    issued_token_type: TokenType = pydantic.Field(
        default=...,
        title="Issued token type",
        description=(
                "An identifier for the representation of the issued security token."
        ),
        example="urn:ietf:params:oauth:token-type:jwt"
    )

    token_type: str = pydantic.Field(
        default=...,
        description=(
            "A case-insensitive value specifying the method of using "
            "the access token issued. It provides the client with "
            "information about how to utilize the access token to "
            "access protected resources.  For example, a value of "
            "`Bearer` indicates that the issued security token is "
            "a bearer token and the client can simply present it "
            "as is without any additional proof of eligibility "
            "beyond the contents of the token itself.  Note that "
            "the meaning of this parameter is different from the "
            "meaning of the `issued_token_type` parameter, which "
            "declares the representation of the issued security "
            "token; the term `token type` is more typically used "
            "to mean the structural or syntactical representation "
            "of the security token, as it is in all `*_token_type` "
            "parameters.  If the issued token is not an access "
            "token or usable as an access token, then the `token_type` "
            "value `N_A` is used to indicate that an OAuth 2.0 "
            "`token_type` identifier is not applicable in that context."
        ),
        example='Bearer'
    )

    expires_in: typing.Optional[int] = pydantic.Field(
        default=None,
        title="Expires in",
        description=(
            "The validity lifetime, in seconds, of the token issued by the "
            "authorization server.  Oftentimes, the client will not have "
            "the inclination or capability to inspect the content of the "
            "token, and this parameter provides a consistent and token-type "
            "agnostic indication of how long the token can be expected to "
            "be valid.  For example, the value 1800 denotes that the "
            "token will expire in thirty minutes from the time the "
            "response was generated."
        ),
        example=1800
    )

    scope: typing.Optional[str] = pydantic.Field(
        default=None,
        description=(
            "Present if the scope of the issued security token is different "
            "to the scope requested by the client; otherwise it is absent."
        ),
        example="foo bar baz"
    )

    refresh_token: typing.Optional[str] = pydantic.Field(
        default=None,
        description=(
            "A refresh token will typically not be issued when the exchange "
            "is of one temporary credential (the subject_token) for a "
            "different temporary credential (the issued token) for use "
            "in some other context.  A refresh token can be issued in "
            "cases where the client of the token exchange needs the "
            "ability to access a resource even when the original "
            "credential is no longer valid (e.g., user-not-present or "
            "offline scenarios where there is no longer any user "
            "entertaining an active session with the client). Profiles "
            "or deployments of this specification should clearly document "
            "the conditions under which a client should expect a refresh "
            "token in response to `urn:ietf:params:oauth:grant-type:token-exchange`"
            " grant type requests."
        )
    )

    class Config:
        title = "Token Exchange Response"
        exclude_defaults = True