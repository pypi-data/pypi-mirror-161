"""Declares a basic session management framework."""
import datetime
import logging
from typing import Any
from typing import Generator

import fastapi
import cryptography.exceptions
from ckms.jose import PayloadCodec
from ckms.types import ClaimSet
from ckms.utils import b64encode_str
from unimatrix.exceptions import CanonicalException

from cbra.conf import settings # type: ignore
from cbra.params import ServerCodec
from cbra.params import CurrentServer
from .basesession import BaseSession
from .const import SESSION_COOKIE_NAME
from .const import SESSION_ENCRYPTION_KEYS
from .const import SESSION_SIGNING_KEYS


class SessionClaims(dict[str, Any]):

    def __init__(self, session: 'CookieSession', *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.session = session

    def update(self, *args: Any, **kwargs: Any):
        self.session.dirty = True
        return super().update(*args, **kwargs)



class CookieSession(BaseSession):
    """Represents a session that a user agent has with the
    authorization server.
    """
    audience: set[str] = set()
    domain: str | None = None
    issuer: str
    logger: logging.Logger = logging.getLogger('uvicorn')
    token: str | None
    token_type: str = "jwt+session"
    readonly: bool = False
    samesite: str = 'strict'

    def __init__(self,
        request: fastapi.Request,
        issuer: str = CurrentServer,
        codec: PayloadCodec = ServerCodec,
        token: str = fastapi.Cookie(
            default=None,
            alias=SESSION_COOKIE_NAME,
            title="Session",
            description=(
                "Identifies the current session associated to the user agent."
            )
        )
    ):
        self.claims = self.awaiting
        self.codec = codec
        self.dirty = set()
        self.issuer = issuer
        self.request = request
        self.token = token
        if request is not None:
            request.scope['session'] = self

    async def add_to_response(self, response: fastapi.Response) -> None:
        """Update the response with the modified session, if it was
        modified during request handling.
        """
        if self.readonly:
            return
        if not self.dirty and not self.created:
            return
        claims = self.claims if self.claims != self.awaiting else {}
        assert isinstance(claims, dict)
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=b64encode_str(
                await self.codec.encode(
                    payload=ClaimSet.parse_obj({
                        **claims,
                        'iss': self.issuer,
                        'aud': self.audience or self.issuer
                    }),
                    signers=SESSION_SIGNING_KEYS,
                    encrypters=SESSION_ENCRYPTION_KEYS,
                    content_type=self.token_type,
                    allow_compact=False,
                    allow_flattened=False
                )
            ),
            max_age=86000 * 365,
            secure=True,
            httponly=True,
            samesite=self.samesite,
            domain=self.domain,
            path=self.path
        )

    async def _deserialize(self) -> None:
        now = int(datetime.datetime.utcnow().timestamp())
        if self.token is None:
            self.created = True
            self.claims = {'iat': now}
        elif self.claims == self.awaiting:
            assert self.token is not None
            try:
                _, claims = await self.codec.jwt(
                    token=str.encode(self.token, 'ascii'),
                    accept="jwt+session"
                )
                claims.verify(
                    audience=self.audience or {self.issuer}
                )
                self.claims = SessionClaims(self, claims.dict())
            except (CanonicalException, cryptography.exceptions.InvalidTag) as exception:
                # The session was tampered with or we rotated the session key.
                self.logger.critical(
                    "Caught %s while decoding session cookie. "
                    "Session was probably tampered with.",
                    type(exception).__name__
                )
                self.created = True
                self.claims = {'iat': now}
            except Exception as exception:
                self.logger.exception("Caught fatal %s", type(exception).__name__)
                self.created = True
                self.claims = {'iat': now}

    async def get(self, key: str) -> Any:
        """Retrieve a key from the session, or ``None`` if it does
        not exist.
        """
        await self # type: ignore
        assert isinstance(self.claims, dict), repr(self.claims)
        return self.claims.get(key) # type: ignore

    async def set(self, key: str, value: Any) -> None:
        """Set a key to the session."""
        if key in self.reserved_keys:
            raise ValueError(f"Reserved session key: {key}")
        await self # type: ignore
        assert isinstance(self.claims, dict)
        if value != self.claims.get(key): # type: ignore
            self.dirty.add(key)
            self.claims[key] = value

    def __await__(self) -> Generator[Any, None, None]:
        return self._deserialize().__await__()
