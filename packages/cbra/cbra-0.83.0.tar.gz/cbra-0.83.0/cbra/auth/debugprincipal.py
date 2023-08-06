"""Declares :class:`DebugPrincipal`."""
from fastapi import Cookie

from cbra.types import IPrincipal
from cbra.utils import docstring


class DebugPrincipal(IPrincipal):
    """An :class:`~cbra.types.IPrincipal` implementation that retrieves
    the subject identifier from a cookie value. Used for testing purposes
    only.

    This principal implementation authenticates a request by looking up
    a cookie (specified by :attr:`cookie_name`) from the request and takes
    the content of the cookie as the subject identifier.
    """
    __module__: str = 'cbra.auth'
    cookie_name: str = 'subject'
    subject_identifier_type: type[int] | type[str] = str

    def __init__(self, sub: str | None = Cookie(None, alias=cookie_name)):
        self.sub = sub or ''

    @docstring(IPrincipal)
    def is_authenticated(self) -> bool:
        return bool(self)

    def __bool__(self) -> bool:
        return self.sub is not None