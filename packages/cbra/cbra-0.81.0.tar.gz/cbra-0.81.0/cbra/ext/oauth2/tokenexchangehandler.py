"""Declares :class:`TokenExchangeHandler`."""
import datetime
import typing

import fastapi
import pydantic

from cbra.ext import ioc
from .exceptions import Error
from .exceptions import UnsupportedSubjectTokenType
from .exceptions import UnsupportedTokenTypeRequested
from .iopenauthorizationserver import IOpenAuthorizationServer
from .isubject import ISubject
from .requestcontext import RequestContext
from .requesthandler import RequestHandler
from .tokenexchangerequest import TokenExchangeRequest
from .tokenexchangeresponse import TokenExchangeResponse
from .tokentype import TokenType


class TokenExchangeHandler(RequestHandler):
    """The base class to implement a handler for an OAuth 2.0
    token exchange as specified in :rfc:`8693`.
    """
    __module__: str = 'cbra.ext.oauth2'
    response_model: typing.Type[pydantic.BaseModel] = TokenExchangeResponse

    @classmethod
    def as_handler(cls, server: IOpenAuthorizationServer, **kwargs):
        """Return a request handler that invokes the handler."""
        async def f(
            dto: TokenExchangeRequest = TokenExchangeRequest.as_dependant(),
            ctx: RequestContext = ioc.instance(RequestContext),
            handler: TokenExchangeHandler = ioc.instance(cls),
        ) -> TokenExchangeResponse:
            handler.setup(**kwargs)
            handler.now = datetime.datetime.utcnow()
            return await handler.handle(ctx, dto)
        f.__doc__ = cls.__doc__
        return f

    async def apply_audience_policy(
        self,
        ctx: RequestContext,
        request: TokenExchangeRequest,
        sub: ISubject,
        scope: typing.Set[str]
    ):
        """Applies the policy for the ``resource`` specified in the token
        exchange request.

        The `ctx` parameter is a :class:`~cbra.ext.oauth2.RequestContext`
        instance describing the metadata of the :class:`TokenRequest`
        `request`.

        The subject identified :attr:`TokenExchangeRequest.subject_token`
        is provided through the `sub` parameter.

        The `scope` parameter is the scope as requested by the client,
        represented as a :class:`set`. To narrow down the scope, call
        the :meth:`set.remove()` method.

        The :meth:`apply_resource_policy` method does not have a return
        value. It is expected to update the `ctx` or `scope` accordingly.
        """
        pass

    async def apply_resource_policy(
        self,
        ctx: RequestContext,
        request: TokenExchangeRequest,
        sub: ISubject,
        scope: typing.Set[str]
    ):
        """Applies the policy for the ``resource`` specified in the token
        exchange request.

        The `ctx` parameter is a :class:`~cbra.ext.oauth2.RequestContext`
        instance describing the metadata of the :class:`TokenRequest`
        `request`.

        The subject identified :attr:`TokenExchangeRequest.subject_token`
        is provided through the `sub` parameter.

        The `scope` parameter is the scope as requested by the client,
        represented as a :class:`set`. To narrow down the scope, call
        the :meth:`set.remove()` method.

        The :meth:`apply_resource_policy` method does not have a return
        value. It is expected to update the `ctx` or `scope` accordingly.
        """
        pass

    async def apply_subject_policy(
        self,
        ctx: RequestContext,
        request: TokenExchangeRequest,
        sub: ISubject,
        scope: typing.Set[str]
    ):
        """Applies the policy that is specific for the subject requesting
        the token exchange.

        The `ctx` parameter is a :class:`~cbra.ext.oauth2.RequestContext`
        instance describing the metadata of the :class:`TokenRequest`
        `request`.

        The subject identified :attr:`TokenExchangeRequest.subject_token`
        is provided through the `sub` parameter.

        The `scope` parameter is the scope as requested by the client,
        represented as a :class:`set`. To narrow down the scope, call
        the :meth:`set.remove()` method.

        The :meth:`apply_subject_policy` method does not have a return
        value. It is expected to update the `ctx` or `scope` accordingly.
        """
        pass

    def can_issue(self, token_type: str) -> bool:
        """Return a boolean indicating if the server can issue the specified
        `token_type`.
        """
        return False

    def get_supported_token_types(self) -> typing.Set[str]:
        """Return the set of token types that the server is able to
        issue.
        """
        return set()

    def get_supported_subject_token_types(self) -> typing.Set[str]:
        """Return the set of subject token types supported."""
        return set()

    async def create_token_response(
        self,
        ctx: RequestContext,
        request: TokenExchangeRequest,
        sub: ISubject,
        scope: typing.Set[str]
    ) -> TokenExchangeResponse:
        """Invoked when all permissions and policies are validated. Create a
        token and return a corresponding :class:`TokenExchangeResponse`
        instance.
        """
        raise NotImplementedError

    async def handle(
        self,
        ctx: RequestContext = ioc.instance(RequestContext),
        dto: TokenExchangeRequest = TokenExchangeRequest.as_dependant()
    ) -> TokenExchangeResponse:
        """Handle an **OAuth 2.0 Token Exchange** request and return the result.
        
        Verify that the ``subject_token`` parameter of the exchange request is
        valid. Proceed to invoke methods enforcing the policies for the current
        subject, resource and audience. Finally, if all checks pass, generate
        the requested token and return it to the client.

        Args:
            ctx (:class:`~cbra.ext.oauth2.RequestContext`): describes the context
                of the current request and maintains state.
            dto (:class:`~cbra.ext.oauth2.TokenExchangeRequest`): the parameters
                of the **OAuth 2.0 Token Exchange** request.

        Raises:
            :exc:`~cbra.ext.oauth2.UnsupportedTokenTypeRequested`: the
                ``requested_token_type`` parameter specified a token type
                that is not supported by the server.
            :exc:`~cbra.ext.oauth2.UnsupportedSubjectTokenType`: the token
                used to identify the subject (``subject_token``) is of a
                type that is not supported by the server.

        Returns:
            :class:`~cbra.ext.oauth2.TokenExchangeResponse`: a datastructure
                holding the exchanged token and additional parameters describing
                the token.
        """
        if dto.actor_token:
            raise Error(
                error="invalid_request",
                error_description="The use of actor tokens is not implemented by this server."
            )
        if not self.can_issue(dto.requested_token_type):
            raise UnsupportedTokenTypeRequested(
                requested=dto.requested_token_type,
                supported=self.get_supported_token_types()
            )
        sub = await self._verify_subject_token(dto.subject_token_type, dto.subject_token)
        scope = dto.scope

        assert sub is not None # nosec
        if dto.resource:
            await self.apply_resource_policy(ctx, dto, sub, scope)
        if dto.audience:
            await self.apply_audience_policy(ctx, dto, sub, scope)
        await self.apply_subject_policy(ctx, dto, sub, scope)
        return await self.create_token_response(ctx, dto, sub, scope)

    async def verify_subject_token(self, token_type: str, token: str):
        """Verifies the ``subject_token`` parameter of the token exchange request. This
        method is expected to return a datastructure describing the subject of the
        token.
        """
        raise NotImplementedError

    async def _verify_subject_token(self, token_type, token):
        supported = self.get_supported_subject_token_types()
        if token_type not in supported:
            raise UnsupportedSubjectTokenType(
                given=token_type,
                supported=supported
            )
        return await self.verify_subject_token(token_type, token)