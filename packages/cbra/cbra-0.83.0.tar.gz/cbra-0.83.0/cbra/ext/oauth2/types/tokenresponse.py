"""Declares :class:`TokenResponse`."""
import pydantic


class TokenResponse(pydantic.BaseModel):
    __module__: str = 'cbra.ext.oauth2.types'

    access_token: str = pydantic.Field(
        title="Access token",
        description="The access token issued by the authorization server.",
        example=(
            "eyJhbGciOiAiRWREU0EiLCAia2lkIjogIjMwNTYzZWE4NmFiYWRlMWVjNWY1NmY0M"
            "GIwNzcyZjVmIiwgInR5cCI6ICJhdCtqd3QifQ.eyJhdWQiOiAiaHR0cHM6Ly9sb2N"
            "hbGhvc3Q6ODAwMCIsICJjbGllbnRfaWQiOiAicHVibGljIiwgImV4cCI6IDE2NDk1"
            "MjY0MzUsICJpYXQiOiAxNjQ5NTI2MTM1LCAiaXNzIjogImh0dHBzOi8vbG9jYWxob"
            "3N0OjgwMDAiLCAianRpIjogImpzeVFUa1dkemxmdy1jUGR6dnFuQV92QjMzbWNtbn"
            "FUIiwgIm5iZiI6IDE2NDk1MjYxMzUsICJzY29wZSI6ICJyZWFkIHdyaXRlIiwgInN"
            "1YiI6ICJib2JAZXhhbXBsZS51bmltYXRyaXhvbmUuaW8ifQ.EDansI-1VepV-l5dJ"
            "79IZolPcE3r2tewZrS91srOiGIhLA9bustHC_htZ4x4nzm0l4RWlaLxq7oA3svYAR"
            "ZblPSoI7GICEprqEblCYT8THn3__Blyeev4Tz9iTc2xvrxrCrompWVGGl2FZRyLkI"
            "-9xIA"
        )
    )

    token_type: str = pydantic.Field(
        title="Token type",
        description=(
            "The type of the token issued.\n\n"
            "The access token type provides the client with the information "
            "required to successfully utilize the access token to make a "
            "protected resource request (along with type-specific "
            "attributes).  The client must not use an access token if it "
            "does not understand the token type."
        ),
        example="Bearer"
    )
    expires_in: int = pydantic.Field(
        title="Expires in",
        description=(
            "The lifetime in seconds of the access token.  For example, the "
            "value `3600` denotes that the access token will expire in one "
            "hour from the time the response was generated."
        ),
        example=3600
    )
    state: str | None = pydantic.Field(
        title="State",
        description=(
            "Present if the `state` parameter was present in the client "
            "authorization request.  The exact value received from the client."
        ),
        example="jG-7nvPJ1-rpvUaTfstRfeA2WRExie1l"
    )

    refresh_token: str | None = pydantic.Field(
        title="Refresh token",
        description="Present if the client allows refresh tokens."
    )

    id_token: str | None = pydantic.Field(
        title="OpenID Connect ID Token",
        description=(
            "An OpenID Connect ID Token if the `response_type` parameter "
            "in the **Authorization Code Flow** was set to `code id_token`, "
            "otherwise `id_token` is absent."
        )
    )