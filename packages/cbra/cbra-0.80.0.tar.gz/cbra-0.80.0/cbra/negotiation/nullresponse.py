"""Declares :class:`DefaultContentNegotiation`."""
from typing import Any

import fastapi

from cbra.renderers import NullRenderer
from cbra.types import IRenderer
from .default import DefaultContentNegotiation


class NullResponseContentNegotiation(DefaultContentNegotiation):
    """A content negotiation implementation that returns a response without a
    body.
    """
    __module__: str = 'cbra.negotiation'

    @classmethod
    def get_response_headers(cls) -> dict[str, Any]:
        return {}

    @classmethod
    def has_response_body(cls) -> bool:
        return False

    def select_renderer(
        self,
        renderers: list[type[IRenderer]],
        format_suffix: str | None = None,
        default: type[IRenderer] | None = None
    ) -> IRenderer:
        """Return a :class:`cbra.renderers.NullRenderer` instance."""
        return NullRenderer("*/*")