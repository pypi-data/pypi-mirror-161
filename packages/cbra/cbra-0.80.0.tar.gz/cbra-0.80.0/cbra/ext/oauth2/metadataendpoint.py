"""Declares :class:`MetadataEndpoint`."""
import cbra

from .types import IAuthorizationServer
from .types import ServerMetadata


class MetadataEndpoint(cbra.Endpoint):
    __module__: str = 'cbra.ext.oauth2'
    require_authentication: bool = False
    summary: str = "Server metadata"
    description: str = (
        "The metadata endpoint returns a JSON datastructure that an OAuth 2.0 "
        "client can use to obtain the information needed to interact with an "
        "OAuth 2.0 authorization server, including its endpoint locations and "
        "authorization server capabilities."
    )
    method: str = "GET"
    response_description: str = (
        "A JSON datastructure describing the authorization server "
        "(see RFC 8414)."
    )
    response_model: type[ServerMetadata] = ServerMetadata
    server: IAuthorizationServer

    async def handle(self) -> ServerMetadata:
        return await self.server.get_metadata(self.request)