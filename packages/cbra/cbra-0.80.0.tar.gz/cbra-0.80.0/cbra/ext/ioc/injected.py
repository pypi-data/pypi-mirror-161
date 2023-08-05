# pylint: disable=W0221,W0223
"""Declares :class:`Injected`."""
import inspect
import typing
from typing import Any
from typing import AsyncGenerator

import fastapi

from .dependency import Dependency
from .provider import _default


NULL = object()


class Injected(Dependency): # pragma: no cover
    """A :class:`cbra.Dependency` implementation that uses the :mod:`ioc`
    module to provide a dependency.
    """
    __module__: str = 'cbra.ext.ioc'
    args: list[Any]
    default: Any
    invoke: bool = False
    kwargs: dict[str, Any]

    def __init__(
        self,
        name: str,
        invoke: bool = False,
        default: typing.Any = NULL
    ):
        self.name = name
        self.invoke = invoke
        self.default = default
        self.args = []
        self.kwargs = {}
        super().__init__(use_cache=True)

    def get_signature(self) -> inspect.Signature:
        """Return a :class:`inspect.Signature` instance representing the
        call sigature of the dependency resolver.
        """
        return inspect.signature(self.__call__)

    async def __call__(self, request: fastapi.Request) -> AsyncGenerator[Any, None]:
        provider = getattr(request.app, 'container', _default)
        if not provider.is_satisfied(self.name) and self.default != NULL:
            dependency = self.default
        else:
            dependency = provider.resolve(self.name)
        yield dependency\
            if not self.invoke or not callable(dependency)\
            else dependency(*self.args, **self.kwargs)

