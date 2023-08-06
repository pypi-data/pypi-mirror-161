"""Declares :class:`IClientRepository`."""
import abc
from typing import Any

from ..exceptions import ClientDoesNotExist
from .configurable import Configurable
from .iclient import IClient


class IClientRepository(Configurable, metaclass=abc.ABCMeta):
    """Specifies the interface for :term:`IClient` repository
    implementations.
    """
    __module__: str = 'cbra.ext.oauth2.types'
    DoesNotExist: type[BaseException] = ClientDoesNotExist
    ClientDoesNotExist: type[BaseException] = DoesNotExist
    kwargs_name: str = 'clients'
    settings_key: str = 'OAUTH_CLIENTS'

    @classmethod
    def new(cls, **kwargs: Any) -> type['IClientRepository']:
        return type(cls.__name__, (cls,), kwargs)

    @abc.abstractmethod
    async def exists(self, client_id: str) -> bool:
        """Retur a boolean indicating if the client exists."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, client_id: str) -> IClient:
        """Lookup an OAuth 2.0 client using its client identifier."""
        raise NotImplementedError