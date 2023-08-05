"""Declares :class:`AuthorizationResponse`."""
import fastapi


class AuthorizationResponse(fastapi.Response):
    __module__: str = 'cbra.ext.oauth2'