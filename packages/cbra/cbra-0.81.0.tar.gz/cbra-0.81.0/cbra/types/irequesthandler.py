"""Declares :class:`IRequestHandler`."""
import datetime
import inspect
import types
import typing

import fastapi
import pydantic

from .icontentnegotiation import IContentNegotiation
from .icorspolicy import ICorsPolicy
from .iparser import IParser
from .iprincipal import IPrincipal
from .irenderer import IRenderer
from .iresponsedigest import IResponseDigest
from .nullquerymodel import NullQueryModel
from .queryoptions import QueryOptions
from .request import Request


class IRequestHandler:
    """The interface for objects that handle a request for a
    specific HTTP method.
    """
    RouterType: typing.Any = typing.Union[
        fastapi.FastAPI,
        fastapi.APIRouter
    ]
    body_methods: typing.Set[str] = {"POST", "PUT", "PATCH"}

    #: Specifies the Cross-Origin Resource Sharing (CORS)
    #: policy used for this endpoint.
    cors_policy: type[ICorsPolicy]

    #: The default digest algorithm if none was selected.
    default_digest: typing.Optional[typing.Type[IResponseDigest]] = None

    #: The default renderer if none was matched based on the content negotiation
    #: headers. If :attr:`default_renderer` is ``None``, then failure to negotiate
    #: a response content type leads to an error response.
    default_renderer: type[IRenderer] | None = None

    default_response_type: str
    default_response: typing.Dict[str, typing.Any]
    default_response_code: int = 200

    #: Description of the endpoint for the OpenAPI schema.
    description: str | None = None

    #: Indicates if there should be automatic documentation.
    document: bool = True

    #: The :class:`cbra.types.IResponseDigest` instance that was selected
    #: to calculate the digest for the response.
    digest: typing.Optional[IResponseDigest] = None

    #: The list of available digest algorithms.
    digest_algorithms: typing.List[typing.Type[IResponseDigest]] = []

    #: The HTTP request method that is handled by the request handler.
    method: str | None = None

    #: Supported HTTP methods by this endpoint implementation.

    #: The :class:`pydantic.BaseModel` implementation used to parse the
    #: request body, or a union thereof.
    model: type[pydantic.BaseModel] | types.UnionType | None = None

    #: The default mount path of the request handler. Must not start with
    #: a slash.
    mount_path: str | None = None

    #: The name through which the request handler can be revered. If not
    #: name is specified, it is generated from the request handler.
    name: str | None = None

    #: The default implementation to negotiate content encoding, langauge
    #: and response digest.
    negotation: type[IContentNegotiation]

    #: The list of parser classes that known how to interpret the
    #: request body, based on the ``Content-Type`` header.
    parsers: list[type[IParser]] = []

    #: The parser that was selected for the current request.
    parser: IParser | None = None

    #: The path at which the request handler is mounted.
    path: str

    #: The authenticated principal of the request.
    principal: IPrincipal | None

    #: Factory function resolving the credentials provided with an
    #: HTTP request (if any, such as session or header authentication)
    #: to a :class:`IPrincipal` implementation.
    principal_factory: typing.Union[
        typing.Callable[..., typing.Optional[IPrincipal]],
        typing.Coroutine[typing.Any, typing.Any, typing.Optional[IPrincipal]],
        typing.Any
    ] = (lambda: None)

    #: Indicates if the endpoint is queryable.
    queryable: bool = False

    #: The current query provided through the request query
    #: parameters.
    query: NullQueryModel

    #: A :class:`fastapi.Request` instance that is being handled
    #: by the request handler.
    request: Request

    #: The list of renderers used to render response bodies.
    renderers: list[type[IRenderer]] = []

    #: The renderer that is current selected for the response.
    renderer: IRenderer | None = None

    #: Indicates if only authenticated requests are allowed.
    require_authentication: bool = False

    #: A mapping of response codes to OpenAPI response descriptions.
    responses: dict[int | str, typing.Any] = {}

    #: Description of the response used in the OpenAPI schema.
    response_description: str = "Success."

    #: The response class that is used by the request handler.
    response_class: type[fastapi.responses.Response] = fastapi.responses.JSONResponse

    #: The response model, if not inferred from the :meth:`handle()`
    #: signature.
    response_model: type[pydantic.BaseModel] | types.UnionType | None = None

    #: Indicates if the response model must be serialized using the aliases
    #: defined on its :class:`pydantic.FieldInfo` members.
    response_model_by_alias: bool = False

    #: Indices if the defaults of the response model must be excluded when
    #: serializing.
    response_model_exclude_defaults: bool = False

    #: Indices if the ``None`` values of the response model must be excluded when
    #: serializing.
    response_model_exclude_none: bool = False

    #: The return type of the method handler (DEPRECATED).
    returns: type[pydantic.BaseModel] | types.UnionType | None = None

    #: The summary shown in the OpenAPI schema.
    summary: str | None = None

    #: OpenAPI tags for the endpoint.
    tags: list[str] = []

    @classmethod
    def add_to_router(
        cls,
        *,
        app: RouterType,
        base_path: str,
        **kwargs: typing.Any
    ) -> None:
        raise NotImplementedError

    @classmethod
    def get_path_signature(cls, detail: bool = False) -> list[inspect.Parameter]:
        return []

    @classmethod
    def get_responses(cls) -> dict[int | str, typing.Any]:
        """Return a mapping associating response codes to OpenAPI
        metadata.
        """
        raise NotImplementedError

    def is_authenticated(self) -> bool:
        """Return a boolean indicating if the request is authenticated."""
        raise NotImplementedError

    def setup(
        self,
        *,
        request: fastapi.Request,
        path: str,
        principal: typing.Optional[IPrincipal],
        parser: IParser,
        renderer: IRenderer,
        cors: ICorsPolicy,
        digest: typing.Optional[IResponseDigest],
        query: typing.Any,
        session: typing.Any
    ) -> None:
        self.cors = cors
        self.digest = digest
        self.parser = parser
        self.path = path
        self.principal = principal
        self.query = query
        self.renderer = renderer
        self.request = request
        self.session = session

    def serialize_response(
        self,
        request: fastapi.Request,
        context: typing.Dict[typing.Any, typing.Any]
    ) -> str:
        raise NotImplementedError

    async def on_exception(
        self,
        request: fastapi.Request,
        exception: Exception
    ) -> fastapi.Response:
        raise NotImplementedError
