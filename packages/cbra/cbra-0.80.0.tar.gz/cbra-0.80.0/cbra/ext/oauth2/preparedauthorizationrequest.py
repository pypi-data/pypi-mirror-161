"""Declares :class:`PreparedRequest`."""
import typing

import fastapi
import fastapi.params
from ckms.jose.exceptions import JOSEException

from cbra.ext.oauth2.iclient import IClient
from .authorizationrequest import AuthorizationRequest
from .codechallenge import CodeChallenge
from .exceptions import Error
from .iopenauthorizationserver import IOpenAuthorizationServer


class PreparedAuthorizationRequest(AuthorizationRequest):
    """A prepared request that is supplied by the client through the
    ``request`` or ``request_uri`` parameter.
    """
    __module__: str = 'cbra.ext.oauth2'

    request: typing.Optional[str] = None
    request_uri: typing.Optional[str] = None

    @classmethod
    def as_dependant(
        cls,
        server: IOpenAuthorizationServer,
        client: fastapi.params.Depends
    ) -> typing.Any:
        """Construct a function with the appropriate signature to inject the
        parameters and return a :class:`PreparedAuthorizationRequest`.
        """
        async def f(
            client: typing.Union[fastapi.params.Depends, IClient] = client,
            dto: AuthorizationRequest = AuthorizationRequest.as_dependant(
                client=client,
                pkce=CodeChallenge.as_dependant()
            ),
            request: str = fastapi.Query(
                default=None,
                title="Request",
                description=(
                    "A JSON Web Token (JWT) that holds an OAuth 2.0 authorization "
                    "request as JWT Claims Set."
                )
            ),
            request_uri: str = fastapi.Query(
                default=None,
                title="Request URI",
                description=(
                    "Absolute URI from which the **Request Object** can be obtained."
                )
            )
        ) -> typing.Any:
            if not request and not request_uri:
                return dto
            params = {
                **await cls.deserialize_par(
                    server=server,
                    client=client,
                    request=await cls.fetch_par(server, client, request_uri)
                ),
                **await cls.deserialize_par(server, client, request),
                **dto.dict(exclude_defaults=True)
            }
            return cls(**params)

        return fastapi.Depends(f)

    @staticmethod
    async def deserialize_par(
        server: IOpenAuthorizationServer,
        client: IClient,
        request: typing.Optional[str] = None
    ) -> typing.Dict[str, typing.Any]:
        """Deserialize the content of a Prepared Authorization Request (PAR)."""
        if request is None:
            return {}
        try:
            return await server.deserialize_jwt(client, request)
        except JOSEException:
            raise Error(
                error_description="The signature of the request could not be verified."
            )

    @staticmethod
    async def fetch_par(
        server: IOpenAuthorizationServer,
        client: IClient,
        request_uri: typing.Optional[str] = None
    ) -> typing.Optional[str]:
        """Fetch a Prepared Authorization Request (PAR) from the remote URI."""
        if request_uri is None:
            return None

        return await server.retrieve_request(client,  request_uri)

    def __bool__(self) -> bool:
        return bool(self.request or self.request_uri)