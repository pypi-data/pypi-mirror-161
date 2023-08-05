"""Declares :class:`IAuthorizationServer`."""
from typing import Any

import fastapi

from .iupstreamprovider import IUpstreamProvider
from .servermetadata import ServerMetadata


class IAuthorizationServer:
    __module__: str = 'cbra.ext.oauth2.types'
    login_endpoint: str | None
    login_url: str | None
    metadata_endpoint: type[Any]
    providers: dict[str, IUpstreamProvider]

    def allows_grant(self, grant_type: str) -> bool:
        """Return a boolean indicating if the server is configured to allow
        the given grant type.
        """
        raise NotImplementedError

    async def get_metadata(self, request: fastapi.Request) -> ServerMetadata:
        """Return a datastructure describing the server endpoints
        and capabilities.
        """
        raise NotImplementedError