"""Declares :class:`QueryRunner`."""
import functools
from typing import Any


class QueryRunner:
    """The base class for all query runners."""
    __module__: str = 'cbra.query'

    async def connect(self):
        """Setup a connection to the persistent storage system or otherwise
        configure the :class:`QueryRunner` to begin executing queries.
        """
        pass

    async def close(self):
        """Close the connection(s) with the persistent storage system(s) and
        release all resources.
        """
        pass

    @functools.singledispatchmethod
    async def execute(self, query: Any) -> Any:
        raise NotImplementedError

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args, **kwargs):
        # Since the QueryRunner never does mutations, no special exception
        # handling is needed on exit.
        await self.close()
