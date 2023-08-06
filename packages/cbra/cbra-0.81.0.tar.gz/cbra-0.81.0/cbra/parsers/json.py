"""Declares :class:`JSONParser`."""
import json
import typing

import fastapi

from cbra.types import IParser
from ..exceptions import ParseError


class JSONParser(IParser):
    """
    Parses JSON-serialized data.
    """
    __module__: str = 'cbra.parsers'
    media_type: str = 'application/json'
    strict: bool    = True
    charset: str    = "utf-8"

    async def parse(self,
        request: fastapi.Request,
        media_type: typing.Optional[str] = None,
        parser_context: typing.Optional[typing.Dict[str, typing.Any]] = None
    ) -> typing.Any:
        """Parses the incoming bytestream as JSON and returns the resulting
        data.
        """
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', self.charset)
        try:
            return json.loads(bytes.decode(await request.body(), encoding))
        except ValueError:
            raise ParseError
