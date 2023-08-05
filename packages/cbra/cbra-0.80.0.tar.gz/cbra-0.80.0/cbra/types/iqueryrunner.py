"""Declares :class:`IQueryRunner`."""
import functools
from typing import Any


class IQueryRunner:
    """Specifies an abstract interface to run read-only data queryies."""
    __module__: str = 'ckms.types'

    @functools.singledispatchmethod
    async def execute(self, query: Any) -> Any:
        """Execute the `query` with the specified parameters."""
        raise NotImplementedError(
            f"No handler was defined for {type(query).__name__}"
        )
