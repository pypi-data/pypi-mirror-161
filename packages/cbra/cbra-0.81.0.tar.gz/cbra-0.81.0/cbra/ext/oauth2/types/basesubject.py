"""Declares :class:`BaseSubject`."""
from collections import defaultdict

from cbra.utils import docstring
from .isubject import ISubject


class BaseSubject(ISubject):
    __module__: str = 'cbra.ext.oauth2.types'
    sub: int | str
    client_id: str | None = None
    scope: set[str] = set()
    client_scope: defaultdict[str | None, set[str]] = defaultdict(set)

    @docstring(ISubject)
    def allows_scope(self, scope: set[str]) -> bool:
        return scope <= self.client_scope[self.client_id]