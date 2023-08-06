"""Declares :class:`YAMLParser`."""
import typing

import fastapi
import yaml

from cbra.types import IParser
from ..exceptions import ParseError


class YAMLParser(IParser):
    """Parses YAML-serialized data."""
    __module__: str = 'cbra.parsers'
    media_type: str = 'application/yaml'
    charset: str    = "utf-8"

    async def parse(self,
        request: fastapi.Request,
        media_type: typing.Optional[str] = None,
        parser_context: typing.Optional[typing.Dict[str, typing.Any]] = None
    ) -> typing.Any:
        """Parses the incoming bytestream as YAML and returns the resulting
        data.
        """
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', self.charset)
        try:
            content = await request.body()
            if content is None:
                return None
            assert content is not None # nosec
            return yaml.safe_load(bytes.decode(content, encoding)) # type: ignore
        except ValueError:
            raise ParseError
