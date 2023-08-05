"""Declares :class:`IStorage`."""
import functools
import typing

from ckms.types import ClaimSet

from ..exceptions import Error
from .authorizationcode import AuthorizationCode
from .authorizationrequest import AuthorizationRequest
from .baseauthorizationrequest import BaseAuthorizationRequest


class IStorage:
    """Declares the interface that storage implementations for the OAuth 2.0
    server need to implement.
    """
    __module__: str = 'cbra.ext.oauth2.types'
    InvalidAuthorizationCode: type[Error] = type('InvalidAuthorizationCode', (Error, ), {
        'error': "invalid_grant",
        'error_description': "The presented authorization code grant is not valid."
    })

    async def consume(self, claims: ClaimSet) -> bool:
        """Consume the claims set, ensuring that its token can only be
        used once. Return a boolean indicating if the token was already
        consumed.
        """
        raise NotImplementedError

    async def get(
        self,
        key: str
    ) -> typing.Optional[typing.Union[bytes, str]]:
        """Return a key from the transient storage backend, or ``None``
        if it does not exist.
        """
        raise NotImplementedError

    async def get_authorization_request(
        self,
        request_id: str
    ) -> AuthorizationRequest:
        """Lookup an authorization request from the transient storage."""
        raise NotImplementedError

    async def get_code(self, code: str) -> tuple[AuthorizationCode, AuthorizationRequest]:
        """Lookup an authorization code."""
        raise NotImplementedError

    async def get_pushed_authorization_request(
        self,
        request_uri: str
    ) -> BaseAuthorizationRequest:
        """Look an authorization request that was pushed through the Pushed
        Authorization Request (PAR) endpoint.
        """
        raise NotImplementedError

    async def set(
        self,
        key: str,
        value: typing.Union[bytes, str],
        expires: typing.Optional[int] = None
    ) -> None:
        """Set a `key` to given `value` to the **transient** storage backend.
        If `value` is a :class:`dict`, then all its members must be
        JSON-serializable.

        The `expires` parameter define the period after which the key expires
        i.e. it should be (automatically) removed from the transient storage
        backend. It is denoted in seconds.
        """
        raise NotImplementedError

    @functools.singledispatchmethod
    async def persist(
        self,
        obj: AuthorizationRequest | AuthorizationCode
    ) -> None:
        """Persist an object to the transient storage."""
        raise NotImplementedError(type(obj).__name__)

    @persist.register
    async def _persist_authorizationcode(
        self,
        obj: AuthorizationCode
    ) -> None:
        return await self.persist_authorizationcode(obj)

    @persist.register
    async def _persist_authorizationrequest(
        self,
        obj: AuthorizationRequest
    ) -> None:
        return await self.persist_authorizationrequest(obj)

    async def persist_authorizationcode(
        self,
        obj: AuthorizationCode
    ) -> None:
        """Persist an :class:`cbra.ext.oauth2.types.AuthorizationCode`
        instance.
        """
        raise NotImplementedError

    async def persist_authorizationrequest(
        self,
        obj: AuthorizationRequest
    ) -> None:
        """Persist an :class:`cbra.ext.oauth2.AuthorizationRequest`
        instance.
        """
        raise NotImplementedError

    async def pop(
        self,
        key: str
    ) -> typing.Optional[typing.Union[bytes, str]]:
        """Like :meth:`get()`, but also removes the key."""
        raise NotImplementedError