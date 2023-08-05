"""Declares :class:`Principal`."""
import dataclasses
import re
import typing

from ckms.types import ClaimSet
from ckms.types import MalformedPayload

from .types import IPrincipal


@dataclasses.dataclass
class Principal(IPrincipal):
    """A basic :class:`~cbra.ext.oauth2.IPrincipal` implementation."""
    sub: typing.Union[int, str]
    client_id: str
    scope: typing.Set[str] = dataclasses.field(
        default_factory=set
    )

    @classmethod
    def fromclaimset(cls, claims: ClaimSet) -> 'Principal':
        assert claims.sub is not None # nosec
        scope = []
        if 'client_id' not in claims.extra:
            raise MalformedPayload(
                message="The JWT must supply the 'client_id' claim."
            )
        if 'scope' in claims.extra:
            if not isinstance(claims.extra['scope'], str):
                raise MalformedPayload(
                    message="The 'scope' parameter must be a string."
                )
            scope = re.split('\\s', claims.extra['scope'])
        return cls(
            client_id=claims.extra['client_id'],
            sub=claims.sub,
            scope=set(scope)
        )

    def has_scope(
        self,
        scope: typing.Union[str, typing.Set[str]]
    ) -> bool:
        """Return a boolean indicating if the :class:`IPrincipal` is
        authorized to use the given `scope`.
        """
        if isinstance(scope, str):
            scope = {scope}
        return self.scope >= scope