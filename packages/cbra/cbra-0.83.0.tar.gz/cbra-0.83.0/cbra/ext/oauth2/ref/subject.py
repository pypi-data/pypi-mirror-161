# pylint: skip-file
from typing import Any
from typing import Coroutine

from ckms.core.models import JSONWebSignature
from ckms.types import JSONWebKeySet
from ckms.types import JSONWebKey

from cbra.ext.oauth2.types import BaseSubject


class Subject(BaseSubject):
    sub: str
    keys: list[JSONWebKey] = []

    @property
    def jwks(self) -> JSONWebKeySet:
        return JSONWebKeySet(keys=self.keys)

    def allows_scope(self, scope: set[str]) -> bool:
        assert isinstance(scope, set)
        if self.client_id is None:
            return False
        return scope <= self.client_scope[self.client_id]

    def register_public_key(self, key: JSONWebKey) -> None:
        self.keys.append(key)

    def verify(
        self,
        jws: JSONWebSignature
    ) -> bool | Coroutine[Any, Any, bool]:
        return jws.verify(self.jwks, require_kid=False)