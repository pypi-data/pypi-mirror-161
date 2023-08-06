"""Declares :class:`BodyDependantModel`."""
import typing

import fastapi
import fastapi.params
import pydantic

from .dependantmodel import DependantModel


class BodyDependantModel(DependantModel):
    __module__: str = 'cbra.ext.oauth2'
    _source_class: typing.Type[pydantic.fields.FieldInfo] = fastapi.params.Body