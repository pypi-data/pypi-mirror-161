"""Declares :class:`Endpoint`."""
import collections
import dataclasses
import functools
import inspect
import logging
import typing
import types
from inspect import signature
from inspect import Parameter
from typing import cast
#from typing import get_args
from typing import Any

import aorta
import fastapi
import fastapi.params
import pydantic
from aorta import MessagePublisher
from fastapi.dependencies.utils import get_dependant
from fastapi.dependencies.utils import get_parameterless_sub_dependant
from fastapi.dependencies.utils import solve_dependencies
from fastapi.dependencies.utils import Dependant

from cbra.digests import SHA256Digest
from cbra.digests import SHA512Digest
from cbra.exceptions import get_exception_response
from cbra.exceptions import AuthenticationRequired
from cbra.exceptions import CanonicalException
from cbra.exceptions import MissingRequestBody
from cbra.exceptions import UncaughtException
from cbra.exceptions import UnprocessableEntity
from cbra.negotiation import DefaultContentNegotiation
from cbra.parsers import JSONParser
from cbra.parsers import FormParser
from cbra.parsers import YAMLParser
from cbra.params import ClientHost
from cbra.renderers import JSONRenderer
from cbra.renderers import YAMLRenderer
from cbra.session import BaseSession
from cbra.session import NullSession
from cbra.types import IContentNegotiation
from cbra.types import ICorsPolicy
from cbra.types import IEndpoint
from cbra.types import IParser
from cbra.types import IPrincipal
from cbra.types import IRenderer
from cbra.types import IResponseDigest
from cbra.types import NullQueryModel
from cbra.types import Request
from cbra.utils import classproperty
from cbra.utils import current_timestamp
from cbra import cors
from .auth import NullPrincipal
from .endpointmetaclass import EndpointMetaclass
from .endpointresolver import EndpointResolver
from .params import ServerPublisher
from .transaction import Transaction
from .utils import order_parameters
from .useragent import UserAgent


class Endpoint(IEndpoint, metaclass=EndpointMetaclass):
    """An endpoint is an abstraction that models the end of a message
    channel through which a system can send or receive messages. The
    :class:`Endpoint` provides a low-level interface to implement such
    termina.
    """
    __abstract__: bool = True
    __module__: str = 'cbra'
    logger: logging.Logger = logging.getLogger('uvicorn')
    now: int

    #: The list of available digest algorithms.
    digest_algorithms: typing.List[typing.Type[IResponseDigest]] = [
        SHA256Digest,
        SHA512Digest
    ]

    #: The :class:`cbra.lib.auth.IPrincipal` implementation that is used
    #: to authenticate and authorize requests to this endpoint.
    principal: IPrincipal = NullPrincipal()

    #: The message publisher for events and commands.
    publisher: MessagePublisher = ServerPublisher

    #: The currently active messaging transaction.
    transaction: Transaction = fastapi.Depends(Transaction)

    #: A :class:`cbra.cors.BaseCorsPolicy` implementation that enforces
    #: the Cross-Origin Resource Sharing (CORS) policy of the server.
    cors_policy: typing.Type[ICorsPolicy] = cors.DefaultPolicy

    #: The default digest algorithm if none was selected.
    default_digest: typing.Type[IResponseDigest] = SHA256Digest

    #: The default response media type, if not specified by the
    #: ``Accept`` request header.
    default_response_type: str = "application/json"

    # The model used to filter a search query.
    filter_model: typing.Any

    #: Resolves the content negotiation class for requests.
    negotiation: typing.Type[IContentNegotiation] = DefaultContentNegotiation

    #: The list of :class:`cbra.types.IParser` implementations that are used
    #: to deserialize the request body.
    parsers: list[type[IParser]] = [
        JSONParser,
        FormParser,
        YAMLParser,
    ]

    #: The plural name of the resource name
    pluralname: str | None = None

    #: The remote host address.
    remote_host: str = ClientHost

    #: The list of renderers used to render response bodies.
    renderers: typing.List[typing.Type[IRenderer]] = [
        JSONRenderer,
        YAMLRenderer
    ]

    #: The session implementation used by this endpoint.
    session: BaseSession

    #: All status codes that may be returned by this endpoint.
    status_codes: set[int] = set()

    #: Fallback renderer to create a response if no content type
    #: could be negotiated.
    fallback_renderer: typing.Type[IRenderer] = JSONRenderer

    @classproperty
    def common_headers(cls) -> dict[str, typing.Any]:
        """The common headers for all responses."""
        return {
            **cls.cors_policy.get_response_headers(),
            **cls.negotiation.get_response_headers()
        }

    @classproperty
    def default_response(cls) -> typing.Dict[str, typing.Any]:
        return {
            'description': cls.response_description, # type: ignore
            'content': {
                x.media_type: {
                    'schema': {}
                } for x in cls.renderers
            },
            'headers': cls.common_headers
        }

    @classproperty
    def openapi_extra(cls) -> dict[str, Any]:
        """The extra OpenAPI schema definition for the request method defined
        by the :class:`Endpoint`.
        """
        if cls.model is None:
            return {}

        # The .model attribute may be either a pydantic.BaseModel or
        # types.UnionType instance. For types.UnionType, all members
        # must be a subclass of pydantic.BaseModel.
        is_model = inspect.isclass(cls.model)\
            and issubclass(cls.model, pydantic.BaseModel)
        is_polymorphic = isinstance(cls.model, types.UnionType)\
            or typing.get_origin(cls.model) == typing.Union
        if not is_model and not is_polymorphic:
            raise ValueError(
                f"{cls.model.__name__} must be a subclass of pydantic.BaseModel " # type: ignore
                "or a types.UnionType instance."
            )

        assert is_model or is_polymorphic
        schema = {}
        if is_model:
            # Simply invoke pydantic.BaseModel.schema() to get the OpenAPI
            # schema.
            assert inspect.isclass(cls.model)
            assert issubclass(cls.model, pydantic.BaseModel)
            schema = cls.model.schema()
        elif is_polymorphic:
            schema = {}

        # Iterate over the parsers defined by Endpoint.parsers to render the
        # OpenAPI content examples.
        content: dict[str, Any] = {}
        for parser in cls.parsers:
            content[parser.media_type] = {
                'schema': schema,
                'example': parser.openapi_example(schema)
            }
        return {
            'requestBody': {
                'content': content
            }
        }

    @classproperty
    def responses(cls) -> dict[str | int, Any]:
        """The responses returned by this endpoint."""
        # The body of a response to an OPTIONS request is assumed
        # to be empty.
        if cls.method == "OPTIONS":
            return {}

        headers = cls.common_headers
        has_body = cls.negotiation.has_response_body()
        defaults = {
            400: get_exception_response(400, headers, has_body),
            401: get_exception_response(401, headers, has_body),
            403: get_exception_response(403, headers, has_body),
            415: get_exception_response(415, headers, has_body),
            422: get_exception_response(422, headers, has_body),
            500: get_exception_response(500, headers, has_body),
            503: get_exception_response(503, headers, has_body),
        }
        if cls.method in {"PATCH", "POST", "PUT"}:
            defaults.update({
                406: get_exception_response(406, headers, has_body)
            })
        return defaults

    @classproperty
    def returns(cls) -> type[pydantic.BaseModel] | types.UnionType | None:
        if cls.response_model:
            response_type = cls.response_model
        else:
            response_type = signature(cls.handle).return_annotation
        return response_type

    @classmethod
    def add_to_router(
        cls,
        *,
        app: IEndpoint.RouterType,
        base_path: str = '/',
        method: str | None = None,
        cors_policy: type[ICorsPolicy] | None = None,
        request_handler: typing.Optional[
            typing.Callable[..., IEndpoint.ResponseTypes]
        ] = None,
        **kwargs: typing.Any
    ) -> None:
        cors_policy = cors_policy or cls.cors_policy or cors.DefaultPolicy
        method = method or cls.method
        if method is None:
            raise ValueError("The `method` parameter can not be None.")
        if not str.startswith(base_path, '/'):
            raise ValueError("The `base_path` parameter must start with a slash.")
        base_path = str.rstrip(base_path, '/')
        if cls.mount_path:
            base_path = f'{base_path}/{cls.mount_path}'
        base_path = base_path or '/'

        cls = cls.new(
            __module__=cls.__module__,
            cors_policy=cors_policy,
            method=method
        )

        endpoint = cls.as_handler(
            method = method,
            path = base_path,
            request_handler = request_handler
        )
        endpoint.__doc__ = (
            kwargs.pop('description', None) or
            cls.description or
            getattr(cls.handle, '__doc__', None)
        )

        kwargs.setdefault('include_in_schema', cls.document)
        kwargs.setdefault('name', cls.name)
        kwargs.setdefault('response_class', cls.response_class)
        kwargs.setdefault('response_description', cls.response_description)
        kwargs.setdefault('response_model', cls.response_model)
        kwargs.setdefault('summary', cls.summary)
        tags = kwargs.setdefault('tags', [])
        if cls.tags:
            tags.extend(cls.tags)
        kwargs['tags'] = list(set(sorted(tags)))
        app.add_api_route(
            dependencies=[fastapi.Depends(cors_policy)],
            path=base_path,
            methods=[method],
            endpoint=endpoint,
            responses={
                **cls.get_responses(),
                **kwargs.pop('responses', {}),
            },
            status_code=cls.default_response_code,
            response_model_by_alias=cls.response_model_by_alias,
            **kwargs
        )

        # TODO: Ugly but we need it now.
        if cls.with_options and cls.method != "OPTIONS":
            from .options import Options
            options = Options.new(
                allowed_methods={cls.method, "OPTIONS"},
                cors_policy=cls.cors_policy,
                document=cls.document,
                is_detail=False,
                model=cls.model,
                name=cls.name,
                summary=cls.summary
            )
            options.add_to_router(
                app=app,
                base_path=base_path,
                tags=cls.tags
            ) # type: ignore

    @classmethod
    def as_handler(
        cls,
        method: str,
        path: str,
        request_handler: typing.Optional[
            typing.Callable[..., IEndpoint.ResponseTypes]
        ] = None
    ) -> typing.Coroutine[typing.Any, typing.Any, IEndpoint.ResponseTypes]:
        """Return a callable that invokes the endpoint handler."""
        hints = typing.get_type_hints(cls)
        QueryModel = hints.get('query') or NullQueryModel
        Session = hints.get('session') or NullSession
        if Session == BaseSession:
            Session = NullSession
        cors_policy = cls.cors_policy
        origin_header = cors_policy.origin_header
        negotiation = cls.negotiation
        if method in {"POST", "PUT", "PATCH"}:
            negotiation = cls.negotiation.with_body
        if method == "OPTIONS":
            cors_policy = cors_policy.as_options

        async def handle(
            request: Request,
            principal: IPrincipal = fastapi.Depends(cls.principal_factory),
            origin: str | None = cast(str | None, origin_header),
            handler: cls = fastapi.Depends(),
            cors: cors_policy = fastapi.Depends(), # type: ignore
            query: QueryModel = fastapi.Depends(QueryModel),
            negotiation: negotiation = fastapi.Depends(), # type: ignore
            useragent: UserAgent = fastapi.Depends(),
            session: BaseSession = fastapi.Depends(Session),
            *args: typing.Any,
            **kwargs: typing.Any
        ) -> IEndpoint.ResponseTypes:
            cors: ICorsPolicy = cors
            negotiation: IContentNegotiation = negotiation
            await cors.process_request(request, handler, origin)
            func = functools.partial(cls.handle, handler)
            if request_handler and request_handler != Ellipsis: # type: ignore
                func = functools.partial(request_handler, handler) # type: ignore
            try:
                handler.request = request
                handler.setup(
                    request=request,
                    principal=principal,
                    path=path,
                    parser=negotiation.select_parser(cls.parsers),
                    renderer=negotiation.select_renderer(renderers=cls.renderers),
                    cors=cors,
                    digest=negotiation.select_digest(
                        cls.digest_algorithms,
                        default=cls.default_digest
                    ),
                    session=session,
                    query=query
                )
                response = await handler.dispatch(func, *args, **kwargs)
            except Exception as exception:
                response = await handler.on_exception(exception)
            else:
                if not isinstance(response, fastapi.Response):
                    response = await handler.render_to_response(
                        content=response
                    )
            assert isinstance(response, fastapi.Response), repr(response) # nosec
            await cors.process_response(request, response, handler, origin)
            handler.process_response(request, response)
            return response

        func = cls.update_signature(handle, cls.handle)
        func.endpoint_class = cls # type: ignore
        func.model = cls.get_body_model(cls.handle) # type: ignore
        return func

    @classmethod
    def get_body_model(
        cls,
        func: typing.Callable[..., Any]
    ) -> type[pydantic.BaseModel] | types.UnionType | None:
        model = cls.model
        if model is None:
            sig = inspect.signature(func)
            args = tuple(sig.parameters.values())
            if len(args) > 1:
                model = args[1].annotation
        return model

    @classmethod
    def get_openapi_schema(cls) -> typing.Dict[str, typing.Any]:
        if not cls.needs_body(None) or not hasattr(cls, 'model'):
            return {}

        schema: typing.Dict[str, typing.Any] = {
            'oneOf': []
        }
        for model in typing.get_args(cls.model):
            if not inspect.isclass(model)\
            or not issubclass(model, pydantic.BaseModel):
                raise TypeError(
                    f"{cls.__name__}.model must be a subclass of "
                    "pydantic.BaseModel or subclass thereof."
                )
            schema['oneOf'].append(model.schema())
        if inspect.isclass(cls.model)\
        and issubclass(cls.model, pydantic.BaseModel):
            schema = cls.model.schema()
        return {
            'requestBody': {
                'content': {
                    p.media_type: {
                        'schema': schema
                    } for p in cls.parsers
                }
            }
        }

    @classmethod
    def get_responses(cls) -> dict[int | str, typing.Any]:
        """Return a mapping associating response codes to OpenAPI
        metadata.
        """
        return {
            **cls.responses,
            cls.default_response_code: cls.default_response,
        }

    @classmethod
    def needs_body(cls, method: typing.Optional[str]) -> bool:
        return (method or cls.method) in cls.body_methods

    @classmethod
    def needs_parameter(cls, p: Parameter) -> bool:
        # Ignore the self parameter and basically anything that is not
        # a fastapi.params.Param instance. Dependencies that are injected
        # through fastapi.Depends and that require request attributes,
        # should be injected in the constructor.
        return not (p.name == 'self' or not isinstance(p.default, fastapi.params.Param))

    @classmethod
    def update_signature(
        cls,
        runner: typing.Any,
        handle: typing.Any
    ) ->  typing.Coroutine[typing.Any, typing.Any, IEndpoint.ResponseTypes]:
        """Update the signature of `runner` to include the dependencies
        declared by `handle`. Remote variable positional and variable
        keyword arguments from the signature. Return `runner` with its
        updated signature.
        """
        sig = signature(runner)
        params = collections.OrderedDict(sig.parameters.items())
        for p in signature(handle).parameters.values():
            if p.name in params: # pragma: no cover
                raise ValueError(f"Duplicate parameter: '{p.name}'.")
            if not cls.needs_parameter(p):
                continue
            params[p.name] = p # pragma: no cover

        for p in cls.get_path_signature():
            params[p.name] = p

        runner.__signature__ = sig.replace(
            parameters=order_parameters([
                p for p in params.values()
                if p.kind not in {
                    Parameter.VAR_POSITIONAL,
                    Parameter.VAR_KEYWORD
                }
            ])
        )
        return runner

    async def authenticate(self) -> typing.NoReturn | None:
        """Hook to perform additional authentication checks in addition
        to :attr:`principal_factory`.
        """
        pass

    async def authorize(self) -> typing.NoReturn | None:
        """Hook to perform authorization checks for the request. Must raise
        an appropriate exception if the request is not authorized. This
        method may specify dependencies.
        """
        pass

    async def enforce_cors_policy(self):
        """Hook to enforce a CORS policy prior to handling a request. This
        method may be overrided if determining the CORS policy is based on
        parameters included in a request.
        """
        pass

    async def setup_transaction(self):
        """Hook to override the configuration of a messaging transaction."""
        pass

    async def dispatch(
        self,
        handle: typing.Callable[..., IEndpoint.ResponseTypes],
        **kwargs: typing.Any
    ) -> IEndpoint.ResponseTypes:
        self.now = current_timestamp()
        if self.require_authentication and not self.is_authenticated():
            raise AuthenticationRequired

        assert self.parser is not None # nosec
        body = await self.parser.parse(self.request)
        dependant = get_dependant(path=self.path, call=handle)
        dependant.dependencies.extend(self.__get_dependants())
        values, errors, tasks, response, _ = await solve_dependencies(
            request=self.request,
            dependant=dependant,
            body=body,
            dependency_overrides_provider=None
        )

        # Collect all errors into an UnprocessableEntity instance.
        # Other errors are fatal and should produce a generic
        # internal server serror.
        for error in errors:
            location = error.loc_tuple()
            if isinstance(error.exc, pydantic.ValidationError):
                raise UnprocessableEntity.fromexc(error.exc)
            elif location == ('body',):
                raise MissingRequestBody
            else:
                raise NotImplementedError(error)

        if tasks or response.status_code:
            raise NotImplementedError(errors, tasks, response)
        async with self.transaction:
            return await handle(**values)

    async def handle(self) -> IEndpoint.ResponseTypes:
        raise NotImplementedError

    async def issue(self, command: aorta.Command) -> None:
        """Issue a command within the context of the transaction running
        for the request handler.
        """
        self.transaction.issue(command)

    async def publish(self, event: aorta.Event) -> None:
        """Publish an event within the context of the transaction running
        for the request handler.
        """
        self.transaction.publish(event)

    async def render_to_response(
        self,
        content: typing.Any
    ) -> fastapi.Response:
        renderer = self.get_renderer()
        return fastapi.Response(
            content=renderer.render(
                data=content,
                renderer_context={
                    'by_alias': self.response_model_by_alias,
                    'exclude_defaults': self.response_model_exclude_defaults,
                    'exclude_none': self.response_model_exclude_none
                }
            ),
            status_code=self.default_response_code
        )

    def get_dependants(self) -> typing.List[typing.Callable[..., typing.Any]]:
        """Return the list of callables that are solved prior to
        invoking the request handler.
        """
        return []

    def get_renderer(self) -> IRenderer:
        return self.renderer or self.fallback_renderer("application/yml;indent=2")

    def get_response_encoding(self) -> str:
        return self.get_renderer().get_response_encoding()

    def get_query_parameters(self) -> dict[str, typing.Any] | None:
        """Return the query parameters as parsed by the :attr:`query_model`."""
        return dataclasses.asdict(self.query) or None

    def is_authenticated(self) -> bool:
        """Return a boolean indicating if the request is authenticated."""
        return bool(self.principal)

    @functools.singledispatchmethod
    async def on_exception( # type: ignore[override]
        self,
        exception: Exception
    ) -> fastapi.Response:
        self.logger.exception("Caught fatal %s", type(exception).__name__)
        return await UncaughtException().handle(
            request=self.request,
            handler=self,
            renderer=self.get_renderer()
        )

    @on_exception.register
    async def on_canonical_exception(
        self,
        exception: CanonicalException
    ) -> fastapi.Response:
        return await exception.handle(
            request=self.request,
            handler=self,
            renderer=self.get_renderer()
        )

    @classmethod
    def register_exception(cls, func: Any):
        return cls.on_exception.register(func) # type: ignore

    def process_response(
        self,
        request: fastapi.Request,
        response: fastapi.Response
    ) -> None:
        """Add headers or apply other transformations to the response.
        It should not be modified after invoking this method.
        """
        if self.renderer is not None:
            if bool(response.body) and self.renderer.has_content():
                response.headers['Content-Type'] = self.get_response_encoding()

        # If the method is not HEAD, OPTIONS add the Digest header.
        if self.digest is not None and self.method not in {"HEAD", "OPTIONS"}\
        and response.body:
            response.headers['Digest'] = self.digest.calculate(response.body)

    def __get_dependants(self) -> typing.List[Dependant]:
        dependants = [
            EndpointResolver(self),
            self.setup_transaction,
            self.authenticate,
            self.authorize,
        ]
        if self.request.method != "OPTIONS":
            dependants.append(self.enforce_cors_policy)
        dependants.extend(self.get_dependants())
        return [
            get_parameterless_sub_dependant(
                depends=fastapi.Depends(func),
                path=self.path
            ) for func in dependants
        ]
