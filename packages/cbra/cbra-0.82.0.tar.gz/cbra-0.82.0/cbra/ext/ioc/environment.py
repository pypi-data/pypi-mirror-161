"""Declares :class:`Environment`."""
import os

from .dependency import Dependency


class Environment(Dependency):
    """A :class:`cbra.Dependency` implementation that points to an environment
    variable.
    """
    __module__: str = 'cbra.ext.ioc'

    def __init__(self, name: str):
        self.name = name
        super().__init__(use_cache=True)

    async def resolve(self):
        return os.getenv(self.name)
