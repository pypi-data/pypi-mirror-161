"""Declares :class:`ServerTokenIssuer`."""
from typing import cast
from typing import Any

from ckms.jose import ClaimSet
from ckms.jose import PayloadCodec

from .types import RFC9068Token


class ServerTokenIssuer:
    """Provides an interface to sign and decrypt tokens using the
    authorization servers' configured default keys and algorithms.
    """
    __module__: str = 'cbra.ext.oauth2'
    algorithm: str
    codec: PayloadCodec
    default_ttl: int = 60
    using: str

    async def issue_access_token(
        self,
        claims: dict[str, Any] | RFC9068Token,
        header: dict[str, Any] | None = None,
        ttl: int | None = None,
        model: type[ClaimSet] = RFC9068Token
    ) -> str:
        """Sign an :rfc:`9068` access token using the default signing
        key configured for the authorization server.
        """
        ttl = ttl or self.default_ttl
        if not isinstance(claims, (RFC9068Token, model)):
            claims = model.strict(ttl=ttl, **claims)
        header = header or {}
        header.setdefault('typ', "at+jwt")
        payload = self.codec.encode(claims)
        jws = await payload.sign(
            algorithm=self.algorithm,
            using=self.using,
            header=header
        )
        return bytes.decode(bytes(jws), 'ascii')