"""Declares :class:`SymbolDependencySpec`."""
import typing
from typing import Any

import pydantic

from ..loader import import_symbol # type: ignore
from .dependencyspec import DependencySpec


class SymbolDependencySpec(DependencySpec):
    """Specifies the configuration format for a dependency that is loaded
    from the qualified name of a Python symbol.
    """
    __module__: str = 'cbra.ext.ioc.models'
    type: typing.Literal['symbol'] = 'symbol'
    qualname: str
    invoke: bool = False
    args: list[Any] = []
    kwargs: dict[str, Any] = {}

    async def resolve(self) -> typing.Any:
        """Resolve the dependency specified by the input parameters."""
        symbol = import_symbol(self.qualname) # type: ignore
        if self.invoke or self.args or self.kwargs:
            symbol = symbol(*self.args, **self.kwargs)
        return symbol
