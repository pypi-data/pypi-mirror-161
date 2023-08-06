"""Declares :class:`IOpenAuthotizationServer`."""
import typing

import fastapi

from .iclient import IClient
from .iclientrepository import IClientRepository
from .servermetadata import ServerMetadata
from .tokentype import TokenType


class IOpenAuthorizationServer:
    """The interface of a class that implements an OAuth 2.0
    server.
    """
    __module__: str = 'cbra.ext.oauth2.types'
    subject_token_verifiers: typing.Dict[str, typing.Any]

    #: A class that is used as the repository for clients.
    clients: type[IClientRepository]

    async def deserialize_jwt(
        self,
        client: IClient,
        token: typing.Union[bytes, str]
    ) -> typing.Dict[str, typing.Any]:
        raise NotImplementedError

    async def get_subject_token_verifier(
        self,
        token_type: TokenType
    ) -> typing.Any:
        """Return a :class:`~cbra.ext.oauth2.BaseSubjectTokenVerifier` that
        is used to verify the ``subject_token`` parameter during an
        :rfc:`8693` OAuth 2.0 Token Exchange.
        """
        raise NotImplementedError

    async def retrieve_request(
        self,
        client: IClient,
        request_uri: str
    ) -> str:
        raise NotImplementedError

    def register_keys(
        self,
        default_signing_key: str,
        default_encryption_key: str,
        keys: typing.Dict[str, typing.Dict[str, typing.Any]]
    ) -> None:
        raise NotImplementedError