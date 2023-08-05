"""Declares :class:`DependencyList`."""
import asyncio
import typing

import pydantic

from .dependency import Dependency


class DependencyList(pydantic.BaseModel):
    """A list of dependencies that can be resolved by the provider."""
    __module__: str = 'cbra.ext.ioc.models'
    force: bool = True
    items: typing.List[Dependency]

    @staticmethod
    async def _resolve(dependency: Dependency) -> typing.Tuple[Dependency, typing.Any]:
        return (dependency, await dependency.resolve())

    async def resolve(self) -> list[tuple[Dependency, typing.Any]]:
        """Resolve all dependencies in the list."""
        futures = [self._resolve(x) for x in self.items]
        return [x for x in await asyncio.gather(*futures)]
