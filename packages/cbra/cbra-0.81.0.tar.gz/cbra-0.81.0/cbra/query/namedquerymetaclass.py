"""Declares :class:`NamedQueryMetaclass`."""
import typing

from .namedqueryargs import NamedQueryArgs


class NamedQueryMetaclass(type):
    reserved_attrs: set = {
        "build",
        "resolve",
        "run",
    }

    def __new__(cls, name, bases, attrs):
        new = super().__new__
        if attrs.get('__abstract__', False):
            return new(cls, name, bases, attrs)
        attrs['__abstract__'] = False
        hints = attrs.get('__annotations__') or {}
        fields = {}
        for k in dict.keys(hints): # pragma: no cover
            if str.startswith(k, '_'):
                continue
            if k in cls.reserved_attrs:
                raise ValueError(f"Attribute `{k}` is a reserved name.")
            if k in attrs:
                fields[k] = attrs.pop(k)
        attrs['parameterless'] = bool(fields)
        attrs['model'] = cls.create_model(
            cls,
            name,
            cls.get_model_bases(cls, bases),
            hints,
            fields
        )

        return new(cls, name, bases, attrs)

    def get_model_bases(cls, bases: typing.List[type]) -> typing.Tuple[type]:
        """Return the bases that are used to construct the query model."""
        parents = [
            b for b in bases
            if isinstance(b, NamedQueryMetaclass)
            and not b.__abstract__
        ]
        return (NamedQueryArgs,) if not parents else (parents[0].model,)

    def create_model(cls,
        name: str,
        bases: typing.List[type],
        hints: dict,
        fields: dict
    ) -> NamedQueryArgs:
        """Construct the model used to validate the query parameters."""
        return type(name, cls.get_model_bases(cls, bases), {
            '__annotations__': hints,
            **fields
        })
