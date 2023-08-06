"""Declares :class:`IEndpoint`."""
import typing

import fastapi
import pydantic
from aorta import MessagePublisher

from .irequesthandler import IRequestHandler


ResponseTypes = typing.Union[
    fastapi.Response,
    pydantic.BaseModel,
    typing.Dict[typing.Any, typing.Any],
    typing.List[typing.Any],
]


class IEndpoint(IRequestHandler):
    __module__: str = 'cbra'
    publisher: MessagePublisher
    ResponseTypes: typing.Any = ResponseTypes

    #: Automatically expose the ``OPTIONS`` method for this :class:`Endpoint`
    with_options: bool = False

    @classmethod
    def as_handler(
        cls,
        method: str,
        path: str,
        request_handler: typing.Optional[
            typing.Callable[..., ResponseTypes]
        ]
    ) -> typing.Coroutine[typing.Any, typing.Any, ResponseTypes]:
        raise NotImplementedError

    @classmethod
    def get_openapi_schema(cls) -> typing.Dict[str, typing.Any]:
        raise NotImplementedError

    @classmethod
    def needs_body(cls, method: typing.Optional[str]) -> bool:
        raise NotImplementedError

    @classmethod
    def new(
        cls,
        **attrs: typing.Any
    ) -> typing.Type['IEndpoint']:
        """Create a new subclass of :class:`Endpoint` with the given
        attributes.
        """
        return type(cls.__name__, (cls,), attrs) # pragma: no cover

    @classmethod
    def update_signature(
        cls,
        runner: typing.Any,
        handle: typing.Any
    ) ->  typing.Coroutine[typing.Any, typing.Any, ResponseTypes]:
        raise NotImplementedError

    async def dispatch(
        self,
        handle: typing.Callable[..., ResponseTypes],
        **kwargs: typing.Any
    ) -> ResponseTypes:
        raise NotImplementedError

    async def handle(self) -> ResponseTypes:
        raise NotImplementedError

    async def render_to_response(
        self,
        content: typing.Any
    ) -> fastapi.Response:
        raise NotImplementedError