"""Declares :class:`ISubject`."""
from typing import Any
from typing import Coroutine

import pydantic
from ckms.core.models import JSONWebSignature
from ckms.types import JSONWebKey


class ISubject(pydantic.BaseModel):
    """Specifies the interface to which all subject implementations
    must provide.
    """
    __module__: str = 'cbra.ext.oauth2.types'

    #: The subject identifier. The type and semantics are implementation specific,
    #: but the concrete implementation must ensure that :attr:`sub` is JSON
    #: serializable.
    sub: int | str

    #: Identifies the client in which the context subject was
    #: instantiated, or ``None``.
    client_id: str | None = None

    #: Used for testing purposes only.
    #client_scope: defaultdict[str, set[str]]

    def allows_scope(self, scope: set[str]) -> bool:
        """Return a boolean indicating that the requested scope `scope`
        was allowed by the subject.
        """
        raise NotImplementedError

    def register_public_key(self, key: JSONWebKey) -> None:
        """Register a public key for the :class:`ISubject`."""
        raise NotImplementedError

    def verify(
        self,
        jws: JSONWebSignature
    ) -> bool | Coroutine[Any, Any, bool]:
        """Verifies a JSON Web Signature (JWS) using the keys that were
        previously registered by the :term:`Subject`.
        """
        raise NotImplementedError