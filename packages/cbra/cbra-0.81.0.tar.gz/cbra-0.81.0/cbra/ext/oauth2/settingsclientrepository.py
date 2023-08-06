"""Declares :class:`SettingsClientRepository`."""
from cbra.conf import settings # type: ignore
from cbra.utils import docstring
from .clientconfig import ClientConfig
from .types import IClient
from .types import IClientRepository


class SettingsClientRepository(IClientRepository):
    """A :class:`~cbra.ext.oauth2.types.IClientRepository` implementation
    that uses the :mod:`cbra` settings module as the source of the OAuth
    clients.
    
    The settings module must declare the ``OAUTH_CLIENTS`` attribute holding
    a dictionary that maps client identifiers (i.e. its keys) to dictionaries
    specifying the configuration for that specific client.
    """
    __module__: str = 'cbra.ext.oauth2'
    clients: dict[str, ClientConfig]
    model: type[ClientConfig] = ClientConfig

    def __init__(self) -> None:
        self.clients = {
            k: self.model.parse_obj({**v, 'client_id': k})
            for k, v in dict.items(getattr(settings, 'OAUTH_CLIENTS', {})) # type: ignore
        }

    @docstring(IClientRepository)
    async def exists(self, client_id: str) -> bool:
        return client_id in self.clients

    @docstring(IClientRepository)
    async def get(self, client_id: str) -> IClient:
        if client_id not in self.clients:
            raise self.ClientDoesNotExist
        return self.clients[client_id]