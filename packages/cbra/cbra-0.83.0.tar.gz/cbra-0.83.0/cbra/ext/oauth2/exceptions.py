"""Declares common OAuth 2.0 exceptions."""
import functools
import typing

import fastapi
import fastapi.responses
import pydantic
from unimatrix.exceptions import CanonicalException

from cbra.exceptions import BaseRedirectingException


__all__ = [
    'ClientAuthenticationFailed',
    'Error',
    'ErrorModel',
    'InvalidClient',
    'LoginRequired',
    'MissingRedirectURL',
    'RedirectForbidden',
    'SubjectDoesNotExist',
    'TokenExchangeTargetRejected',
    'UnsupportedTokenTypeRequested',
    'UnsupportedResponseType',
    'UnsupportedSubjectTokenType',
]


class LoginRequired(BaseRedirectingException):
    """Raised when the resource owner needs to authenticate with
    the authorization server.
    """
    __module__: str = 'cbra.ext.oauth2.exceptions'


class ErrorModel(pydantic.BaseModel):
    error: str
    error_description: typing.Optional[str] = None
    error_uri: typing.Optional[str] = None


class Error(Exception):
    error: str = "invalid_request"
    error_description: str
    mode: str = 'client'
    state: str | None = None

    @classmethod
    def as_redirect(cls, redirect_uri: typing.Any) -> 'Error':
        return cls(redirect_uri=redirect_uri)

    @classmethod
    def catch(
        cls,
        error: typing.Type[BaseException],
        description: typing.Optional[str] = None
    ) -> typing.Callable[..., typing.Any]:
        def decorator_factory(func: typing.Any) -> typing.Callable[..., typing.Any]:
            @functools.wraps(func)
            async def decorated(*args: typing.Any, **kwargs: typing.Any):
                try:
                    return await func(*args, **kwargs)
                except error as exc:
                    msg = description
                    if isinstance(exc, CanonicalException) and not msg:
                        msg = exc.message or exc.code
                    if callable(description):
                        msg = typing.cast(str, description(exc))
                    raise cls(error_description=msg)
            return decorated
        return decorator_factory

    def __init__(self, **kwargs: str | typing.Any):
        kwargs.setdefault('error', self.error)
        kwargs.setdefault('error_description', self.get_error_description(**kwargs))
        self.mode = kwargs.pop('mode', self.mode)
        self.state = kwargs.pop('state', None)
        self._redirect_uri = kwargs.pop('redirect_uri', None)
        self._error = ErrorModel(
            error=typing.cast(str, kwargs['error']),
            error_description=typing.cast(str, kwargs['error_description'])
        )

    async def as_response(
        self,
        request: fastapi.Request,
        mode: str | None = None,
        state: str | None = None
    ) -> fastapi.responses.JSONResponse | fastapi.responses.RedirectResponse:
        """Return a :class:`fastapi.responses.Response` instance
        representing the error.
        """
        state = state or self.state
        mode = mode or self.mode
        if mode == 'client' or not self._redirect_uri:
            return fastapi.responses.JSONResponse(
                self._error.dict(exclude_defaults=True),
                status_code=400
            )
        else:
            params = {
                'error': self._error.error,
                'error_description': self._error.error_description
            }
            if state is not None:
                params['state'] = state
            return fastapi.responses.RedirectResponse(
                self._redirect_uri.authorize(**params),
                status_code=303
            )

    def get_error_description(self, **kwargs: str) -> str:
        """Return the error description."""
        return kwargs.get('error_description') or self.error_description

    def must_redirect(self) -> bool:
        return self.mode == 'redirect'


class ClientAuthenticationFailed(Error):
    """Raised when the client credentials could not be authenticated."""
    __module__: str = 'cbra.ext.oauth2'
    error: str = "invalid_request"
    error_description: str = (
        "The client could not be authenticated using the given credentials."
    )


class InvalidGrant(Error):
    __module__: str = 'cbra.ext.oauth2'
    error: str = "invalid_grant"


class AssertionReplayed(InvalidGrant):
    """Raised when the credential is not valid because its replayed."""
    __module__: str = 'cbra.ext.oauth2'
    error_description: str = (
        "The assertion provided by the client was used previously to "
        "obtain an access token. Do not reuse assertions."
    )


class RedirectForbidden(Error):
    """Raised when the ``redirect_uri`` parameter is not valid
    for the given client.
    """
    error: str = "invalid_request"
    error_description: str = (
        "The client does not allow redirects to the URL supplied as "
        "the redirect_uri query parameter."
    )


class MissingRedirectURL(Error):
    error: str = "invalid_request"
    error_description: str = (
        "The `redirect_uri` parameter was not provided and the client "
        "did not specify a default."
    )


class RequestNotSupported(Error):
    error: str = "request_not_supported"
    error_description: str = (
        "The server does not support the use of the `request` or "
        "`request_uri` parameters."
    )


class InvalidClient(Error):
    error: str = "invalid_request"
    error_description: str = (
        "Specify the `client_id` parameter in the request body "
        "if the client is public, else provide credentials with "
        "the `Authorization` header."
    )


class InvalidScope(Error):
    error: str = "invalid_scope"
    error_description: str = (
        "The requested scope exceeds the scope that was granted by the "
        "resource owner."
    )


class ForbiddenScope(Error):
    error: str = "invalid_scope"
    error_description: str = (
        "The client application is not allowed or not allowing use of "
        "the requested scope."
    )


class ClientDoesNotExist(InvalidClient):
    """Like :exc:`InvalidClient`, but explicitely indicates that the
    client does not exist.
    """
    __module__: str = 'cbra.ext.oauth2'
    error_description: str = "The specified client does not exist."


class ClientAuthenticationRequired(InvalidClient):
    """Raised when there is an issued with authenticating a condfidential
    OAuth 2.0 client."""
    __module__: str = 'cbra.ext.oauth2'
    error: str = "invalid_client"
    error_description: str = "The specified client requires authentication."


class InvalidClientAuthenticationScheme(ClientAuthenticationRequired):
    """Raised when the client used the wrong authentication scheme."""
    __module__: str = 'cbra.ext.oauth2'

    def __init__(self, using: str, required: str):
        super().__init__(
            error_description=(
                "Invalid authentication scheme. The server supports "
                f"{required} authentication for confidential clients."
            )
        )


class NoSuchClient(InvalidClient):
    """Raised during a request to the Token Endpoint when the client
    could not be determined from any factor.
    """
    __module__: str = 'cbra.ext.oauth2'
    error: str = "invalid_client"
    error_description: str = (
        "The client specified by the request parameters does not exist."
    )


class UnsupportedTokenTypeRequested(Error):
    """Raised when an unsupported token type is requested."""

    def __init__(self, requested: str, supported: list, **kwargs):
        Error.__init__(
            self,
            error="invalid_request",
            error_description=(
                "The server is unable to issue a token of the requested type: "
                f"{requested}. Supported token types are: "
                f"{str.join(',', sorted(supported))}."
            ),
            **kwargs
        )


class UnsupportedSubjectTokenType(Error):
    """Raised when an unsupported token type is provided."""

    def __init__(self, given: str, supported: list, **kwargs):
        Error.__init__(
            self,
            error="invalid_request",
            error_description=(
                "The server is unable to process a token of the provided type: "
                f"{given}. Supported token types are: "
                f"{str.join(',', sorted(supported))}."
            ),
            **kwargs
        )


class SubjectDoesNotExist(Error):
    """Raises when a lookup for a :term:`Subject` is attempted
    but the search query did not produce a result.
    """
    __module__: str = 'cbra.ext.oauth2'
    error: str = "invalid_request"
    error_description: str = (
        "The principal attached to the request did not resolve "
        "to a subject."
    )


class TokenExchangeTargetRejected(Error):
    """Raised when the server does not allow a specific audience or resource that
    is requested during a token exchange.
    """

    def __init__(self, target: str, message: typing.Optional[str] = None, **kwargs):
        Error.__init__(
            self,
            error="invalid_target",
            error_description=message or (
                f"The target {target} rejected the claims, scope or subject of "
                "the token exchange."
            ),
            **kwargs
        )


class UnsupportedResponseType(Error):
    __module__: str = 'cbra.ext.oauth2'
    error: str = (
        "The requested response type is not supported by the "
        "client or server."
    )
    error_description: str = (
        "Consult the documentation for the supported "
        "response types."
    )
    mode: str = 'redirect'


class CrossOriginNotAllowed(Error):
    error: str = "invalid_origin"
    error_description: str = (
        "Security measures prevent the authorization server from "
        "responding to requests from this domain, because it has "
        "not been whitelisted by the system administrator for use "
        "with this application."
    )
    mode: str = 'redirect'