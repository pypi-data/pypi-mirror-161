"""Declares :class:`NullContentNegotiation`."""
from typing import Any

from cbra.parsers import NullParser
from cbra.renderers import NullRenderer
from cbra.types import IParser
from cbra.types import IRenderer
from .default import DefaultContentNegotiation


class NullContentNegotiation(DefaultContentNegotiation):
    """Completely disables all forms of content negotiation."""

    @classmethod
    def get_response_headers(cls) -> dict[str, Any]:
        return {}

    @classmethod
    def has_response_body(cls) -> bool:
        return False

    @classmethod
    def with_body(cls) -> 'NullContentNegotiation': # type: ignore
        return cls()

    def __init__(self):
        pass

    def select_parser(self, *args, **kwargs) -> IParser: # type: ignore
        return NullParser()

    def select_renderer(self, *args, **kwargs) -> IRenderer: # type: ignore
        return NullRenderer("*/*")