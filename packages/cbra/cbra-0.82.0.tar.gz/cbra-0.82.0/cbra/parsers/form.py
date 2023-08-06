"""Declares :class:`FormParser`."""
import urllib.parse

import fastapi

from cbra.types import IParser


class FormParser(IParser):
    """
    Parser for form data.
    """
    __module__: str = 'cbra.parsers'
    media_type: str = 'application/x-www-form-urlencoded'
    charset: str = "utf-8"

    async def parse(self,
        request: fastapi.Request,
        media_type: str = None,
        parser_context: dict = None
    ) -> dict:
        """Parses the incoming bytestream as a URL encoded form, and returns
        the resulting dictionary.
        """
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', self.charset)
        body = bytes.decode(await request.body(), encoding)
        return {k: v for k, v in urllib.parse.parse_qsl((body or ''), True)}
