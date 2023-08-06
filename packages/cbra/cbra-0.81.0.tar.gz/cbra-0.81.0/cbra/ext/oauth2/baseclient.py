"""Declares :class:`BaseClient`."""
import typing

import fastapi

from cbra.ext import ioc
from .exceptions import ClientDoesNotExist
from .exceptions import InvalidClient
from .types import IClient
from .types import IClientRepository


class BaseClient(IClient):
    """The base class for all OAuth 2.0 client implementations."""
    __module__: str = 'cbra.ext.oauth2'

    @classmethod
    def fromdict(cls, params: dict[str, typing.Any]) -> 'IClient':
        return cls(**params)

    @classmethod
    def fromquery(
        cls,
        clients: type,
        required: bool = False
    ) -> typing.Any:
        """Return a callable that resolves the current client from the
        query parameters.
        """
        async def f(
            client_id: str = fastapi.Query(
                default=... if required else None,
                title="Client ID",
                description=(
                    "A client identifier unique to this authorization server."
                )
            ),
            clients: IClientRepository = ioc.instance(clients)
        ) -> typing.Optional[IClient]:
            if client_id is None and required:
                raise InvalidClient
            try:
                return await clients.get(client_id)
            except ClientDoesNotExist:
                if required:
                    raise
                return None

        return fastapi.Depends(f)