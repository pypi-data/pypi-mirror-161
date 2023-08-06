"""Declares :class:`NullPrincipal`."""
from cbra.types import IPrincipal
from cbra.utils import docstring


class NullPrincipal(IPrincipal):
    """An :class:`~cbra.types.IPrincipal` implementation that is used
    with non-authenticated requests.

    This is the default principal for all endpoints that did not specify
    otherwise.
    """
    __module__: str = 'cbra.auth'

    def __init__(self):
        self.sub = None

    @docstring(IPrincipal)
    def is_authenticated(self) -> bool:
        return False

    def __bool__(self) -> bool:
        return False