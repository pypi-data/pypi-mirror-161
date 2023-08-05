"""Declares :class:`JSONRenderer`."""
import json
import typing

import pydantic

from cbra.encoders import JSONEncoder
from cbra.types import IRenderer
from cbra.utils import parse_header


class JSONRenderer(IRenderer):
    """Renderer which serializes to JSON."""
    __module__: str = 'cbra.renderers'
    charset: typing.Optional[str] = None
    compact: bool = True
    encoder_class: type[JSONEncoder] = JSONEncoder
    ensure_ascii: bool = True
    format: str = 'json'
    indent: typing.Optional[int] = None
    media_type: str = 'application/json'
    response_media_type: str = "application/json"
    strict: bool = True
    structured: bool = True

    def has_content(self) -> bool:
        return True

    def get_indent(
        self,
        accepted_media_type: str,
        renderer_context: typing.Dict[str, typing.Any]
    ) -> typing.Optional[int]:
        if self.accepted:
            _, params = parse_header(self.accepted.encode('ascii'))
            try:
                indent = typing.cast(int, params['indent']) # type: ignore
                v = max(min(int(indent), 8), 0)
                return None if v == 0 else v
            except (KeyError, ValueError, TypeError):
                pass

        # If 'indent' is provided in the context, then pretty print the result.
        return renderer_context.get('indent', None) or self.indent

    def render(
        self,
        data: dict[str, typing.Any] | pydantic.BaseModel,
        renderer_context: dict[str, typing.Any] | None = None
    ) -> bytes:
        """Render `data` into JSON, returning a bytestring."""
        if data is None:
            return b''

        renderer_context = renderer_context or {}
        indent = self.get_indent(self.accepted, renderer_context)
        if indent is None:
            separators = (',', ':')
        else:
            separators = (', ', ': ')

        ret = None
        if isinstance(data, pydantic.BaseModel):
            ret = data.json(
                indent=indent,
                ensure_ascii=self.ensure_ascii,
                allow_nan=not self.strict,
                separators=separators,
                by_alias=renderer_context.get('by_alias'),
                exclude_defaults=renderer_context.get('exclude_defaults'),
                exclude_none=renderer_context.get('exclude_none'),
            )
        else:
            ret = json.dumps(
                data,
                cls=self.encoder_class,
                indent=indent,
                ensure_ascii=self.ensure_ascii,
                allow_nan=not self.strict,
                separators=separators
            )

        # We always fully escape \u2028 and \u2029 to ensure we output JSON
        # that is a strict javascript subset.
        # See: https://gist.github.com/damncabbage/623b879af56f850a6ddc
        ret = ret.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
        return ret.encode()
