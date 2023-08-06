"""Declares :class:`UpstreamProvider`."""
import fastapi

from .types import AuthorizationRequestParameters
from .types import IStorage
from .types import IUpstreamProvider


class UpstreamProvider(IUpstreamProvider):
    __module__: str = 'cbra.ext.oauth2'

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
        return await storage.get_authorization_request(
            request_id=self.get_authorization_request_id(request=request)
        )

    def get_client_redirect(
        self,
        request: fastapi.Request,
        dto: AuthorizationRequestParameters
    ) -> str:
        """Get the client redirect URL."""
        return dto.authorize()

    async def on_return(
        self,
        storage: IStorage,
        request: fastapi.Request
    ) -> fastapi.responses.RedirectResponse:
        params = await self.get_authorization_request(
            storage=storage,
            request=request
        )
        await self.process_response(request, params)
        return fastapi.responses.RedirectResponse(
            url=self.get_client_redirect(
                request=request,
                dto=params
            ),
            status_code=303
        )

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
        return request.url_for(f'oauth2.callback', provider=self.name)