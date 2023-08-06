"""Declares :class:`NullRenderer`."""
import warnings
from typing import Any

import pydantic

from cbra.types import IRenderer


class NullRenderer(IRenderer):
    """
    Renderer which serializes to JSON.
    """
    __module__: str = 'cbra.renderers'

    def has_content(self) -> bool:
        return False

    def render(
        self,
        data: dict[str, Any] | pydantic.BaseModel,
        renderer_context: dict[str, Any] | None = None
    ) -> bytes:
        """Return a an empty byte-string, indicating no response body."""
        if bool(data):
            warnings.warn(f"{type(self).__name__} can not render any content.")
        return b''