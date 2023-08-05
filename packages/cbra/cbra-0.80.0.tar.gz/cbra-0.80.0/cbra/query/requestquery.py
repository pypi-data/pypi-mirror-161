"""Declares :class:`RequestQuery`."""
import inspect
import typing
from inspect import Parameter
from inspect import Signature

import fastapi
import fastapi.params

from cbra.ext.ioc import Parameterless
from .namedquery import NamedQuery
from .pathfield import PathField
from .queryrunner import QueryRunner
from .requestquerymetaclass import RequestQueryMetaclass


class RequestQuery(NamedQuery, metaclass=RequestQueryMetaclass):
    """A :class:`cbra.query.NamedQuery` implementation that discovers its
    parameters from an incoming HTTP request.
    """
    __module__: str = 'cbra.query'

    @classmethod
    def get_query_parameters(cls) -> typing.List[Parameter]:
        params = []
        fields = cls.model.__fields__['args'].type_.__fields__
        for name, field in dict.items(fields):
            kwargs = {
                k: getattr(field.field_info, k)
                for k in field.field_info.__slots__
            }
            Source = fastapi.Path\
                if isinstance(field.field_info, PathField)\
                else fastapi.Query

            kwargs.setdefault('alias', name)
            params.append(
                Parameter(
                    name=name,
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=Source(**kwargs),
                    annotation=field.type_
                )
            )
        return params

    def build(self,
        request: fastapi.Request,
        offset: int = fastapi.Query(default=0),
        limit: int = fastapi.Query(default=100),
        **kwargs
    ):
        """Build the query from the request parameters."""
        return self.model(
            limit=limit,
            offset=offset,
            args=kwargs
        )

    def get_signature(self) -> Signature:
        """Return a :class:`inspect.Signature` instance representing the
        call sigature of the dependency resolver.
        """
        sig = super().get_signature()
        params = list(sig.parameters.values())
        params.extend(self.get_query_parameters())
        return inspect.Signature([
            x for x in params
            if x.kind not in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD)
        ])

    def get_request_dependencies(
        self
    ) -> typing.List[typing.Union[fastapi.params.Path, fastapi.params.Query]]:
        """Return the list of dependencies that are resolved from a
        :class:`fastapi.Request` instance.
        """
        return [
            Parameterless(x.name, x.default, x.annotation)
            for x in self.get_query_parameters()
        ]

    async def _run(self,
        runner: QueryRunner,
        request: fastapi.Request,
        offset: int,
        limit: int,
        *args,
        **kwargs
    ):
        return await super()._run(runner, request, offset, limit, **kwargs)
