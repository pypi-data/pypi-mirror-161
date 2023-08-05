"""Declares :class:`MemoryStorage`."""
import typing

from ckms.types import ClaimSet

from .types import AuthorizationCode
from .types import AuthorizationRequest
from .types import IStorage


class MemoryStorage(IStorage):
    """A :class:`~cbra.ext.oauth2.IStorage` implementation
    that used the local memory. For testing purposes only.
    """
    __module__: str = 'cbra.ext.oauth2'
    objects: typing.Dict[str, typing.Any | AuthorizationCode | AuthorizationRequest] = {}

    def __init__(self):
        self.objects = MemoryStorage.objects

    @classmethod
    def clear(cls) -> None:
        MemoryStorage.objects = {}

    async def consume(self, claims: ClaimSet) -> bool:
        """Consume the claims set, ensuring that its token can only be
        used once. Return a boolean indicating if the token was already
        consumed.
        """
        k = f'consumed.{claims.jti}'
        is_consumed = True
        if k not in self.objects:
            self.objects[k] = ...
            is_consumed = False
        return is_consumed

    async def get_authorization_request(self, request_id: str) -> AuthorizationRequest:
        return self.objects[request_id]

    async def get_code(self, code: str) -> tuple[AuthorizationCode, AuthorizationRequest]:
        try:
            obj = typing.cast(AuthorizationCode, self.objects[code])
            return obj, self.objects[obj.request_id]
        except KeyError:
            raise self.InvalidAuthorizationCode

    async def persist_authorizationrequest(
        self,
        obj: AuthorizationRequest
    ) -> None:
        assert obj.request_id # nosec
        self.objects[obj.request_id] = obj

    async def persist_authorizationcode(self, obj: AuthorizationCode) -> None:
        assert obj.code
        self.objects[obj.code] = obj