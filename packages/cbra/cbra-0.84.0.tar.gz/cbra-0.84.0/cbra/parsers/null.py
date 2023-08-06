"""Declares :class:`NullParser`."""
import typing

import fastapi

from cbra.types import IParser


class NullParser(IParser):
    __module__: str = 'cbra.parser'

    async def parse(self,
        request: fastapi.Request,
        media_type: typing.Optional[str] = None,
        parser_context: typing.Optional[typing.Dict[str, typing.Any]] = None
    ) -> typing.Any:
        return None