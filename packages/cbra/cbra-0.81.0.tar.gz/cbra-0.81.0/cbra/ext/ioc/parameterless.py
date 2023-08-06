"""Declares :class:`Parameterless`."""
import inspect
import typing

import fastapi.params

from .dependency import Dependency


class Parameterless(Dependency):
    """A :class:`Dependency` implementation that represents a parameterless
    depenency.
    """
    __module__: str = 'cbra.ext.ioc'

    @property
    def __signature__(self) -> inspect.Signature:
        return inspect.Signature([self.as_parameter()])

    def __init__(
        self,
        name: str,
        param: typing.Union[fastapi.params.Param, inspect._empty],
        annotation: typing.Optional[typing.Type[type]] = None
    ):
        self.annotation = annotation
        self.name = name
        self.param = param
        super().__init__(use_cache=True)

    def as_parameter(self) -> inspect.Parameter:
        return inspect.Parameter(
            name=self.name,
            kind=inspect.Parameter.KEYWORD_ONLY,
            default=self.param,
            annotation=self.annotation
        )

    async def resolve(self, **kwargs) -> typing.Any:
        return kwargs[self.name]

    def __repr__(self) -> str: # pragma: no cover
        return f"Parameterless({self.name}: {self.annotation.__name__})"
