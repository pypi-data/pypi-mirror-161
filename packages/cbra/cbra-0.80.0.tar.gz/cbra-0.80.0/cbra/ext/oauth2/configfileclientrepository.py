"""Declares :class:`ConfigFileClientRepository`."""
import os
import pathlib
import re
import typing

import aiofiles
import yaml

from .clientconfig import ClientConfig
from .types import IClient
from .types import IClientRepository


class ConfigFileClientRepository(IClientRepository):
    """A :class:`~cbra.ext.oauth2.types.IClientRepository` implementation
    that loads client configuration from a directory on the local fileststem.
    """
    __module__: str = 'cbra.ext.oauth2'
    base_dir: pathlib.Path = pathlib.Path(
        os.path.join(os.getcwd(), 'etc/oauth2')
    )
    caching: bool = True
    clients: dict[str, IClient] = {}
    model: type[IClient] = ClientConfig
    pattern: re.Pattern[str] = re.compile(r'^[A-Za-z0-9\-\_]+$')

    def __init__(self) -> None:
        self.clients = {}
        if self.caching:
            self.clients = ConfigFileClientRepository.clients

    async def exists(self, client_id: str) -> bool:
        """Retur a boolean indicating if the client exists."""
        if not self.pattern.match(client_id):
            return False
        fn = self.base_dir.joinpath(f'{client_id}.yml')
        return fn.exists()

    async def get(self, client_id: str) -> IClient:
        """Lookup an OAuth 2.0 client from a configuration file
        stored in the :attr:`ConfigFileClientRepository.base_dir`
        directory.
        """
        if not self.pattern.match(client_id):
            raise self.ClientDoesNotExist
        if client_id not in self.clients:
            fn = self.base_dir.joinpath(f'{client_id}.yml')
            if not fn.exists():
                raise self.ClientDoesNotExist
            async with aiofiles.open(fn, 'r') as f: # type: ignore
                params = yaml.safe_load(await f.read()) # type: ignore
                params = typing.cast(dict[str, typing.Any], params)
            client = self.model.fromdict({**params, 'client_id': client_id})
            self.clients[client_id] = client
        return self.clients[client_id]