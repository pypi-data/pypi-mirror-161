"""Declares :class:`MemoryClientRepository`."""
import typing

from .types import IClient
from .types import IClientRepository


class MemoryClientRepository(IClientRepository):
    """A :class:`IClientRepository` implementation that used local
    memory for storage. Mainly for testing purposes.
    """
    __module__: str = 'cbra.ext.oauth2'
    clients: typing.Dict[typing.Union[int, str], IClient] = {}

    @classmethod
    def add(cls, client: IClient) -> None:
        """Add a client to the repository."""
        cls.clients[client.client_id] = client

    @classmethod
    def clear(cls) -> None:
        """Clears the repository of all data."""
        cls.clients = {}

    @classmethod
    def configure(cls, clients: typing.Dict[str, IClient]) -> None:
        """Load a mapping of client identifiers to clients."""
        cls.clients.update(clients) # type: ignore

    def __init__(self):
        self.clients = MemoryClientRepository.clients

    async def exists(self, client_id: str) -> bool:
        return client_id in self.clients

    async def get(self, client_id: str) -> IClient:
        try:
            client = self.clients[client_id]
            return client
        except KeyError:
            raise self.ClientDoesNotExist