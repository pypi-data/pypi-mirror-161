"""Declares :class:`ErrorProducer.`"""
import typing

from .exceptions import Error


class ErrorProducer:
    __module__: str = 'ckms.ext.oauth2'

    def reject_request(self, description: typing.Optional[str] = None):
        """Reject the token exchange request with an error state of
        `invalid_request`.
        """
        self._reject("invalid_request", description)

    def reject_target(self, description: typing.Optional[str] = None):
        """Reject the token exchange request with an error state of
        `invalid_target`.
        """
        self._reject("invalid_target", description)

    def _reject(self, code, description, url=None):
        raise Error(
            error=code,
            error_description=description,
            error_uri=url
        )