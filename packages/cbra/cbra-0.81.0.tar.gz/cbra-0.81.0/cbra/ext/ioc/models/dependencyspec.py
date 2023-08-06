"""Declares :class:`DependencySpec`."""
import typing

import pydantic


class DependencySpec(pydantic.BaseModel):
    """The base class for all dependency specifications."""
    __module__: str = 'cbra.ext.ioc.models'
    type: str
    name: str

    async def resolve(self) -> typing.Any:
        """Resolve the dependency specified by the input parameters."""
        raise NotImplementedError
