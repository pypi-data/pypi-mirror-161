"""Declares :attr:`AuthorizationRequestClient`."""
from typing import Optional
from typing import TypeAlias

import fastapi
import pydantic

from .exceptions import Error
from .types import IClient
from .types import IClientRepository
from .params import ClientRepository


__all__ = [
    'AuthorizationRequestClient'
]


ClientIdentifierType: TypeAlias = pydantic.constr(max_length=63)


async def get_authorization_request_client(
    client_id: Optional[ClientIdentifierType] = fastapi.Query(
        default=None,
        title="Client ID",
        description="Identifies the client."
    ),
    clients: IClientRepository = ClientRepository
) -> IClient:
    if client_id is None or not await clients.exists(client_id):
        raise Error(
            error="invalid_request",
            error_description=(
                "The client_id parameter is required an must point to "
                "an existing client."
            )
        )
    return await clients.get(client_id)


AuthorizationRequestClient: IClient = fastapi.Depends(get_authorization_request_client)