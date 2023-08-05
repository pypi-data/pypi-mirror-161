"""Declares :class:`IRenderer`."""
import typing


Renderable = typing.Union[
    typing.Dict[typing.Any, typing.Any],
    typing.List[typing.Any]
]


class IRenderer:
    """All renderers should extend this class, setting the `media_type`
    and `format` attributes, and override the `.render()` method.
    """
    __module__: str = 'cbra.types'
    accepted: str
    media_type: str
    format: typing.Optional[str] = None
    charset: typing.Optional[str] = 'utf-8'
    render_style: str = 'text'
    Renderable: typing.Any = Renderable
    structured: bool = False
    response_media_type: typing.Optional[str] = None
    exact: bool = True

    @classmethod
    def configure(cls, **kwargs: typing.Any) -> typing.Type['IRenderer']:
        return type(cls.__name__, (cls,), kwargs)

    def __init__(self, accepted: str):
        self.accepted = accepted

    def render(
        self,
        data: Renderable,
        renderer_context: typing.Optional[typing.Dict[str, typing.Any]] = None
    ) -> typing.Union[bytes, str]:
        raise NotImplementedError('Renderer class requires .render() to be implemented')

    def has_content(self) -> bool:
        """Return a boolean indicating if the renderer produces content
        at all.
        """
        raise NotImplementedError

    def get_response_encoding(self) -> str:
        assert self.response_media_type is not None # nosec
        return self.response_media_type