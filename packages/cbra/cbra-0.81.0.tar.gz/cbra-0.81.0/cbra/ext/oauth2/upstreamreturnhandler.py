"""Declares :class:`UpstreamReturnHandler`."""
import fastapi
import pydantic

from .params import CurrentUpstreamProvider
from .params import TransientStorage
from .types import AuthorizationRequestParameters
from .types import IStorage
from .types import IUpstreamReturnHandler
from .types import IUpstreamProvider


class UpstreamReturnHandler(IUpstreamReturnHandler):
    __module__: str = 'cbra.ext.oauth2'

    @classmethod
    def add_to_router(
        cls,
        *,
        app: fastapi.FastAPI,
        base_path: str
    ) -> None:
        query_class = cls.query_model or pydantic.BaseModel

        async def handler(
            request: fastapi.Request,
            handler: cls = fastapi.Depends(),
            provider: IUpstreamProvider = CurrentUpstreamProvider(cls.provider),
            storage: IStorage = TransientStorage,
            params: query_class = fastapi.Depends()
        ) -> fastapi.Response:
            handler.storage = storage
            return await handler.handle(
                request=request,
                provider=provider,
                params=params
            )

        app.add_api_route(
            path=f'{base_path}/{cls.provider}',
            endpoint=handler,
            name=f'oauth2.callback.{cls.provider}',
            summary=cls.summary,
            description="Callback URL for external identity provider.",
            methods=['GET']
        )

    async def get_authorization_request(
        self,
        provider: IUpstreamProvider,
        request: fastapi.Request
    ) -> AuthorizationRequestParameters:
        return await provider.get_authorization_request(
            storage=self.storage,
            request=request
        )

    async def handle(
        self,
        *,
        request: fastapi.Request,
        provider: IUpstreamProvider,
        params: pydantic.BaseModel
    ) -> fastapi.Response:
        """Handles the redirect from the upstream identity provider and
        redirects the client to the URI specified in the authorization
        request.
        """
        authorize = await self.get_authorization_request(
            provider=provider,
            request=request
        )
        await provider.process_response(authorize, params)
        return fastapi.responses.RedirectResponse(
            url=provider.get_client_redirect(
                request=request,
                dto=authorize
            ),
            status_code=303
        )