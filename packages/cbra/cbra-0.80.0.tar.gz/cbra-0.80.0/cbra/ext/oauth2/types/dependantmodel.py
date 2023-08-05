"""Declares :class:`DependantModel`."""
from __future__ import annotations
import typing
from inspect import isclass
from inspect import Parameter
from inspect import Signature

import fastapi
import fastapi.params
import pydantic


class DependantModel(pydantic.BaseModel):
    __module__: str = 'cbra.ext.oauth2.types'
    _exclude: typing.Set[str] = set()
    _source_class: typing.Type[pydantic.fields.FieldInfo] = fastapi.params.Query

    @classmethod
    def null(cls) -> None:
        return None

    @classmethod
    def as_dependant(cls, *args: typing.Any, **defaults: typing.Any) -> typing.Any:
        params: typing.List[Parameter] = []
        fields: typing.Dict[str, pydantic.fields.ModelField] = cls.__fields__
        for name, field in fields.items():
            if name in cls._exclude:
                continue
            kwargs = {
                k: getattr(field.field_info, k)
                for k in field.field_info.__slots__
            }
            kwargs.setdefault('alias', name)

            if name in defaults:
                default = defaults.pop(name)
            else:
                default = cls._source_class(**kwargs)
            if isclass(field.type_) and issubclass(field.type_, DependantModel):
                default = fastapi.Depends(field.type_.as_dependant())
            params.append(
                Parameter(
                    name=name,
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=default,
                    annotation=field.type_
                )
            )

        async def f(**kwargs: typing.Any):
            return cls(**kwargs)
        
        f.__signature__ = Signature( # type: ignore
            parameters=params
        )
        return f

    @classmethod
    def fromquery(cls, **kwargs: typing.Dict[str, typing.Any]) -> typing.Any:
        raise NotImplementedError