"""Declares :class:`AuthorizationRequest`."""
from .baseauthorizationrequest import BaseAuthorizationRequest


Base = BaseAuthorizationRequest.query()


class AuthorizationRequestParameters(Base):

    @property
    def request_id(self) -> str | None:
        """Return the request identified as specified by the :attr:`request_uri`
        parameter.
        """
        if self.request_uri is None\
        or not str.startswith(self.request_uri, 'urn:ietf:params:oauth:request_uri'):
            return None
        *_, request_id = str.rsplit(self.request_uri, ':', 1)
        return request_id

    def is_external(self) -> bool:
        """If the request is a reference, return a boolean indicating if the
        request is made available at an external source.
        """
        return not str.startswith(
            self.request_uri or '',
            "urn:ietf:params:oauth:request_uri"
        )

    def is_object(self) -> bool:
        """Return a boolean indicating if the parameters contain a request
        object, supplied by the :attr:`request` parameter.
        """
        return self.request is not None

    def is_reference(self) -> bool:
        """Return a boolean indicating if the authorization request is a
        reference.
        """
        return self.request_uri is not None

    async def resolve(self):
        """Resolves the parameters based on the ``request`` and
        ``request_uri`` parameters.
        """
        pass