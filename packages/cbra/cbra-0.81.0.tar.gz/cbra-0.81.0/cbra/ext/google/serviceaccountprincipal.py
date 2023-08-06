"""Declares :class:`ServiceAccountPrincipal`."""
import dataclasses

from cbra.types import IPrincipal


@dataclasses.dataclass
class ServiceAccountPrincipal(IPrincipal):
    """Represents a principal that is a Google service account."""
    sub: str
    email: str

    def is_authenticated(self) -> bool:
        return True