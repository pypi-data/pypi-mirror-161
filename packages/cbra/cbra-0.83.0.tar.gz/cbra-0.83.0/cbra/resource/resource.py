"""Declares :class:`Resource`."""
import typing
from inspect import Parameter
from typing import Any
from typing import Callable

from cbra.endpoint import Endpoint
from cbra.exceptions import get_exception_headers
from cbra.headers import CORS_HEADERS
from cbra.headers import DIGEST_SCHEMA
from cbra.headers import HEADERS_RESPONSE_BODY
from cbra.types import IEndpoint
from cbra.utils import classproperty
from .action import Action
from .filteroption import FilterOption
from .iresource import IResource
from .pathparameter import PathParameter
from .resourcemetaclass import ResourceMetaclass


class Resource(Endpoint, metaclass=ResourceMetaclass):
    __module__: str = 'cbra.resource'
    __abstract__: bool = True
    action: str
    default_limit: int = 100
    document: bool = True
    filter_actions: list[str] = ['list']
    filter_defaults: list[FilterOption] = [
        FilterOption(
            alias='offset',
            default=0,
            title="Offset",
            annotation=int,
            description="The offset applied to the search query."
        ),
        FilterOption(
            alias='limit',
            default=100,
            title="Limit",
            annotation=int,
            description=(
                "Limits the number of results included in the result set."
            )
        ),
        FilterOption(
            attname="order_by",
            alias='order-by',
            default=[],
            title="Order by",
            annotation=list[str],
            description="Specifies the ordering keys for the query."
        )
    ]
    filter_options: list[FilterOption] = []
    is_detail: bool = False
    parent: type[IResource] | None = None
    path_parameter: typing.Union[str, PathParameter]
    require_authentication: bool = True
    subresources: list[type['Resource']] = []
    verbose_name: str
    verbose_name_plural: str


    @staticmethod
    def foo(
        name: str,
        summary: str | None = None
    ) -> Callable[..., Any]:
        def decorator_factory(func: Callable[..., Any]):
            setattr(func, 'action', {
                'name': name,
                'summary': summary
            })
            return func
        return decorator_factory

    @classproperty
    def default_response(cls) -> typing.Dict[str, typing.Any]:
        return {
            'description': cls.response_description,
            'content': {
                x.media_type: {} for x in cls.renderers
            },
            'headers': {
                **CORS_HEADERS,
                **HEADERS_RESPONSE_BODY,
                'Digest': DIGEST_SCHEMA
            }
        }

    @classmethod
    def add_to_router( # type: ignore
        cls, *,
        app: IEndpoint.RouterType,
        base_path: str = '/',
        method: str = ...,
        request_handler: typing.Optional[
            typing.Callable[..., IEndpoint.ResponseTypes]
        ] = None,
        **kwargs: typing.Any
    ) -> None:
        if request_handler is ...:
            return super().add_to_router(
                app=app,
                base_path=base_path,
                cors_policy=cls.cors_policy,
                method=method,
                operation_id=str.lower(f'{cls.pluralname}.{cls.action}'),
                include_in_schema=cls.document,
                **kwargs
            )

        # Construct the base path based on the resource plural name.
        # All paths are relative to this path.
        assert cls.pluralname is not None # nosec
        base_path = f"{str.rstrip(base_path, '/')}/{str.lower(cls.pluralname)}"

        cls = typing.cast(typing.Type[IResource], cls)
        for action in Action.fromclass(cls):
            action.add_to_router(app=app, base_path=base_path)

        # If there are subresources, the parent must define the
        # path_parameter attribute; subresources are always relative
        # to a detail URL.
        if cls.subresources:
            if not cls.path_parameter:
                raise ValueError(
                    f"For {cls.__module__}.{cls.__name__} to have "
                    f"subresources the {cls.__name__}.path_parameter "
                    "must be declared as a string value specifying "
                    "the parameter name."
                )

            child_mount: str = cls.path_parameter.get_path( # type: ignore
                base_path=str.rstrip(base_path, '/'),
                subpath=None,
                is_detail=True
            )

            # Construct subresource classes using the attributes from
            # the parent.
            for child in cls.subresources:
                if child.path_parameter == cls.path_parameter:
                    raise ValueError(
                        "Child path parameter must be different from parent."
                    )
                child.add_to_router(app=app, base_path=child_mount)

    @classmethod
    def get_path_signature(cls, detail: bool = False) -> list[Parameter]:
        params: list[Parameter] = []
        if detail or cls.is_detail:
            assert isinstance(cls.path_parameter, PathParameter)
            cls.path_parameter.insert_in(params)
        while cls.parent:
            cls = cls.parent
            assert isinstance(cls.path_parameter, PathParameter)
            cls.path_parameter.insert_in(params)
        return params

    def get_path_params(self) -> typing.Dict[str, typing.Any]:
        return typing.cast(
            typing.Dict[str, typing.Any],
            self.request.path_params # type: ignore
        )

    @classmethod
    def get_responses(cls) -> dict[int, typing.Any]:
        responses = super().get_responses()
        if cls.is_detail:
            responses[404] = {
                'headers': get_exception_headers(404),
                'description': (
                    "The resource specified by the path parameter(s) does not exist."
                )
            }
        return responses

    @classmethod
    def needs_parameter(cls, p: Parameter):
        needs_parameter = super().needs_parameter(p)
        return needs_parameter and (p.annotation != cls.model)

    @classmethod
    def update_signature(
        cls,
        runner: typing.Any,
        handle: typing.Any
    ) -> typing.Coroutine[typing.Any, typing.Any, IEndpoint.ResponseTypes]:
        runner = typing.cast(
            IResource,
            super().update_signature(runner, handle)
        )
        return runner

    def reverse(self, action: str, **params: Any) -> str:
        """Reverse the URL for the given action."""
        return self.request.url_for(str.lower(f'{self.name}.{action}'), **params)