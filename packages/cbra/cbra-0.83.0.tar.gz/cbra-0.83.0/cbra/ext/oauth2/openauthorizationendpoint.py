"""Declares :class:`OpenAuthorizationEndpoint`."""
import inspect
import typing

import cbra
from .iopenauthorizationserver import IOpenAuthorizationServer


class OpenAuthorizationEndpoint(cbra.handler.BaseRequestHandler):
    __module__: str = 'cbra.ext.oauth2'
    server: IOpenAuthorizationServer
    handler_class: typing.Type[typing.Any]
    handler: typing.Callable[..., typing.Any]

    @property
    def __signature__(self) -> inspect.Signature:
        return inspect.signature(self.handler)

    def __init__(
        self,
        server: IOpenAuthorizationServer,
        handler_class: typing.Type[typing.Any]
    ):
        self.server = server
        self.handler_class = handler_class
        self.handler = handler_class.as_handler(
            server=self.server,
            metadata=self.server.metadata
        )

    async def __call__(self, *args, **kwargs) -> typing.Any:
        """Resolve dependencies and invoke the handler."""
        return await self.handler(*args, **kwargs)