"""Declares :class:`IUpstreamProvider`."""
import fastapi

from .authorizationrequestparameters import AuthorizationRequestParameters
from .istorage import IStorage


class IUpstreamProvider:
    __module__: str = 'cbra.ext.oauth2.types'
    name: str

    async def create_redirect(
        self,
        request: fastapi.Request,
        dto: AuthorizationRequestParameters
    ) -> str:
        """Create the redirect URI that initiates the authentication and/or
        authorization flow at the upstream identity provider.
        """
        raise NotImplementedError

    async def get_authorization_request(
        self,
        storage: IStorage,
        request: fastapi.Request
    ) -> AuthorizationRequestParameters:
        """Return an authorization request based on the return parameters
        provided by the upstream identity provider.
        """
        raise NotImplementedError

    def get_authorization_request_id(self, request: fastapi.Request) -> str:
        """Discover the authorization request identifier based on the
        return parameters sent by the upstream provider.
        """
        raise NotImplementedError

    def get_client_redirect(
        self,
        request: fastapi.Request,
        dto: AuthorizationRequestParameters
    ) -> str:
        """Get the client redirect URL."""
        raise NotImplementedError

    async def on_return(
        self,
        storage: IStorage,
        request: fastapi.Request
    ) -> fastapi.responses.RedirectResponse:
        """Invoked when the upstream identity provider returns to the
        authorization server.
        """
        raise NotImplementedError

    async def process_response(
        self,
        request: fastapi.Request,
        params: AuthorizationRequestParameters
    ) -> None:
        """Handles the response data from the upstream provider."""
        raise NotImplementedError

    def reverse(self, request: fastapi.Request) -> str:
        """Get the return URL to which the upstream identity
        provider must redirect.
        """
        raise NotImplementedError
