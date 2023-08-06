"""Declares :class:`BrowserRenderer`."""
import typing

from .yaml import YAMLRenderer


class BrowserRenderer(YAMLRenderer):
    """Like :class:`YAMLRenderer`, but uses ``text/plain`` as output
    since most browsers don't support YAML.
    """
    media_type: str = 'text/html'
    exact: bool = False

    def render(self, *args, **kwargs) -> typing.Any: # type: ignore
        content = super().render(*args, **kwargs)
        return f'<html><head></head><body><pre>{content}</pre></body></html>'