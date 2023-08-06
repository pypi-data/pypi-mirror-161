"""Declares :class:`ListQueryResult`."""
import typing

import pydantic


class ListQueryResult(pydantic.BaseModel):
    __module__: str = 'cbra.query'

    total: int
    offset: int
    limit: int = 100
    objects: typing.List[dict] = []
