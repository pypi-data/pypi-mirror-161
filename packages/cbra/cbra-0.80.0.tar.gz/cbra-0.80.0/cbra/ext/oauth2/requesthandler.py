"""Declares :class:`RequestHandler`."""
import abc
import datetime
import typing

import pydantic

from .openauthorizationendpoint import OpenAuthorizationEndpoint


class RequestHandler(metaclass=abc.ABCMeta):
    __module__: str = 'cbra.ext.oauth2'

    #: A callable that returns a :class:`pydantic.BaseModel` holding the
    #: response parameters.
    response_model: typing.Optional[typing.Type[pydantic.BaseModel]] = None

    #: Autoritative date for the request.
    now: datetime.datetime

    @classmethod
    def as_endpoint(
        cls,
        **kwargs: typing.Any
    ) -> OpenAuthorizationEndpoint:
        """Return a callable that handles an incoming request to the OAuth 2.0
        handler.
        """
        return OpenAuthorizationEndpoint(cls, **kwargs)

    def _setup(self, **kwargs: typing.Any):
        self.now = datetime.datetime.utcnow()
        self.setup(**kwargs)

    def setup(self, *args: typing.Any, **kwargs: typing.Any):
        """Hook to configure a handler instance. This method received the
        keyword arguments that were passed to :meth:`as_endpoint()`.
        """
        pass