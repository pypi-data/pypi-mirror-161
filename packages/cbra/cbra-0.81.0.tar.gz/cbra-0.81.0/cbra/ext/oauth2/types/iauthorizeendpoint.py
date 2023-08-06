"""Declares :class:`IAuthorizeEndpoint`."""
from cbra.types import IPrincipal
from .authorizationrequest import AuthorizationRequest
from .authorizationrequestparameters import AuthorizationRequestParameters
from .iclient import IClient
from .istorage import IStorage
from .isubject import ISubject
from .isubjectrepository import ISubjectRepository


class IAuthorizeEndpoint:
    __module__: str = 'cbra.ext.oauth2.types'
    queryable: bool = True
    redirect_uri: str | None
    client: IClient
    issuer: str
    storage: IStorage
    subjects: ISubjectRepository

    async def create_redirect(
        self,
        dto: AuthorizationRequestParameters
    ) -> str:
        raise NotImplementedError

    async def get_subject(
        self,
        client: IClient,
        principal: IPrincipal,
        dto: AuthorizationRequest
    ) -> ISubject | None:
        """Return a :class:`~cbra.ext.oauth2.types.ISubject` instance
        representing the currently authenticated principal.
        """
        raise NotImplementedError

    async def persist(
        self,
        dto: AuthorizationRequest
    ) -> None:
        """Inspect the request parameters and persist the appropriate
        objects to the transient storage.
        """
        raise NotImplementedError

    async def validate_request(
        self,
        client: IClient,
        subject: ISubject,
        dto: AuthorizationRequest
    ) -> None:
        """Validates an OAuth 2.0 authorization request."""
        raise NotImplementedError