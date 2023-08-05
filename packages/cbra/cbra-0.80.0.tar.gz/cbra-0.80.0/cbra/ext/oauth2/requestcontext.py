"""Declares :class:`RequestContext`."""
import secrets
import typing

import fastapi


class RequestContext:
    __module__: str = 'cbra.ext.oauth2'

    @property
    def issuer(self) -> str:
        """The OAuth 2.0/OpenID Connect issuer, based on the
        current HTTP request.
        """
        return f'{self.request.url.scheme}://{self.request.url.netloc}'

    def __init__(self, request: fastapi.Request):
        self.request_id = secrets.token_bytes(24)
        self.request = request
