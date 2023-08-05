"""Declares :class:`IUpstreamReturnHandler`."""
import fastapi
import pydantic

from .authorizationrequestparameters import AuthorizationRequestParameters
from .istorage import IStorage
from .iupstreamprovider import IUpstreamProvider


class IUpstreamReturnHandler:
    __module__: str = 'cbra.ext.oauth2.types'
    provider: str
    summary: str
    query_model: type[pydantic.BaseModel] | None = None
    storage: IStorage

    @classmethod
    def add_to_router(
        cls,
        *,
        app: fastapi.FastAPI | fastapi.APIRouter,
        base_path: str
    ) -> None:
        raise NotImplementedError

    async def get_authorization_request(
        self,
        provider: IUpstreamProvider,
        request: fastapi.Request
    ) -> AuthorizationRequestParameters:
        """Return the authorization request for which we are handling
        a redirect from the external identity provider.
        """
        raise NotImplementedError