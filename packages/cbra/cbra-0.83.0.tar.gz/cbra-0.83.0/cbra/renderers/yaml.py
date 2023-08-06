"""Declares :class:`YAMLRenderer`."""
import typing

import pydantic
import yaml

from .json import JSONRenderer


class YAMLRenderer(JSONRenderer):
    """
    Renderer which serializes to YAML.
    """
    __module__: str = 'cbra.renderers'
    format: str = 'yaml'
    media_type: str = 'application/yaml'
    response_media_type: str = "application/yaml"
    #encoder_class = encoders.JSONEncoder

    def has_content(self) -> bool:
        return True

    def render(
        self,
        data: dict[str, typing.Any] | pydantic.BaseModel,
        renderer_context: dict[str, typing.Any] | None = None
    ) -> bytes:
        """Render `data` into YAML, returning a bytestring."""
        if data is None:
            return b''
        assert data is not None # nosec
        serialized = yaml.safe_dump( # type: ignore
            data,
            indent=self.get_indent(self.accepted, renderer_context or {}),
            default_flow_style=False
        )
        return '---\n' + serialized # type: ignore
