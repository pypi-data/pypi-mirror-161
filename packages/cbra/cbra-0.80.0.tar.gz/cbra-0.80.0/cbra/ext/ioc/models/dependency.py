"""Declares :class:`Dependency`."""
import typing

import pydantic

from .filedependencyspec import FileDependencySpec
from .symboldependencyspec import SymbolDependencySpec


class Dependency(pydantic.BaseModel):
    """The specification of a dependency."""
    __module__: str = 'cbra.ext.ioc.models'
    force: typing.Optional[bool] = None
    spec: typing.Union[
        FileDependencySpec,
        SymbolDependencySpec
    ]

    async def resolve(self) -> typing.Any:
        """Resolve the dependency as defined in the specification."""
        return await self.spec.resolve()
