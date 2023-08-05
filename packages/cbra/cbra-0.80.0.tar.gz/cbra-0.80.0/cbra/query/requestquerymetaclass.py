"""Declares :class:`RequestQueryMetaclass`."""
import typing

import pydantic

from .namedqueryargs import NamedQueryArgs
from .namedquerymetaclass import NamedQueryMetaclass


class RequestQueryMetaclass(NamedQueryMetaclass):

    def create_model(
        cls,
        name: str,
        bases: typing.List[type],
        hints: dict,
        fields: dict
    ) -> NamedQueryArgs:
        """Construct the model used to validate the query parameters."""
        return type(
            f'Request{name}',
            (pydantic.BaseModel,),
            {
                'limit': 100,
                'offset': 0,
                '__annotations__': {
                    'args' :super().create_model(cls, name, bases, hints, fields),
                    'limit': int,
                    'offset': int
                }
            }
        )
