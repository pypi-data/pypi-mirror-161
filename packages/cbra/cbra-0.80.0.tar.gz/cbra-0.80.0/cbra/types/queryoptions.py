"""Declares :class:`QueryOptions`"""
import inspect
import typing

import fastapi
import pydantic


class QueryOptions(pydantic.BaseModel):
    offset: typing.Optional[int] = 0
    limit: typing.Optional[int] = 100
    order_by: typing.Optional[typing.List[str]] = []

    @classmethod
    def is_reserved_field(cls, name: str) -> bool:
        return name in {'offset', 'limit', 'order_by'}

    @classmethod
    def null(cls) -> typing.Optional['QueryOptions']:
        return None

    @classmethod
    def as_dependant(cls) -> typing.Callable[..., 'QueryOptions']:

        def query_factory(**kwargs: typing.Any) -> cls:
            return cls(**kwargs)

        params = [
            inspect.Parameter(
                name='offset',
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=str,
                default=fastapi.Query(
                    default=0,
                    alias='offset',
                    title="Offset",
                    description=(
                        "The offset that should be applied to the total result "
                        "set matching the search criteria."
                    )
                )
            ),
            inspect.Parameter(
                name='limit',
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=str,
                default=fastapi.Query(
                    default=100,
                    alias='limit',
                    title="Limit",
                    description="Limit the number of objects in the result set."
                )
            ),
            inspect.Parameter(
                name='order_by',
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=typing.List[str],
                default=fastapi.Query(
                    default=[],
                    alias='order-by',
                    title="Order by",
                    description="Specifies attributes to order the results by."
                )
            ),
        ]
        params.extend(cls.get_factory_parameters())
        setattr(
            query_factory,
            '__signature__',
            inspect.Signature(parameters=params, return_annotation=cls)
        )

        return query_factory

    @classmethod
    def get_factory_parameters(cls) -> typing.List[inspect.Parameter]:
        """Update the signature of :meth:`query()` to reflect the
        attributes of the model.
        """
        params: typing.List[inspect.Parameter] = []
        for attname, field in cls.__fields__.items():
            if cls.is_reserved_field(attname):
                continue
            params.append(
                inspect.Parameter(
                    name=attname,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=field.field_info.extra.get('annotation'),
                    default=fastapi.Query(
                        default=field.default,
                        alias=field.alias,
                        title=field.field_info.title,
                        description=field.field_info.description
                    )
                )
            )
        return params