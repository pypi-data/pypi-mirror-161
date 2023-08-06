"""Declares :class:`ICanonicalException`."""
import fastapi

from .icontentnegotiation import IContentNegotiation
from .irenderer import IRenderer
from .irequesthandler import IRequestHandler


class ICanonicalException:

    async def handle(
        self,
        request: fastapi.Request,
        handler: IRequestHandler,
        negotiation: IContentNegotiation,
        renderer: IRenderer
    ) -> fastapi.Response:
        raise NotImplementedError