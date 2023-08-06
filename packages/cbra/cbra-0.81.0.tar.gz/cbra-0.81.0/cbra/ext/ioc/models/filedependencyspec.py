"""Declares :class:`FileDependencySpec`."""
import typing

import aiofiles

from .dependencyspec import DependencySpec


class FileDependencySpec(DependencySpec):
    """The configuration of a dependency that is loaded from a file."""
    __module__: str = 'cbra.ext.ioc.models'
    type: typing.Literal['file'] = 'file'
    path: str

    async def resolve(self) -> typing.Any:
        """Resolve the dependency specified by the input parameters."""
        async with aiofiles.open(self.path, 'rb') as fp: # pylint: disable=C0103
            return await fp.read()
