"""Declares :class:`IResource`."""
import typing

import fastapi.params

from cbra.types import IEndpoint
from .pathparameter import PathParameter


class IResource(IEndpoint):
    __module__: str = 'cbra.resource'
    document: bool = True
    filter_actions: list[str] = ['list']
    filter_options: list[fastapi.params.Query] = []
    is_detail: bool
    method: str
    model: typing.Any = None
    name: str
    name_article: str
    parent: type['IResource'] | None = None
    pluralname: str
    path_parameter: typing.Union[str, PathParameter]
    path_parameter_class: typing.Type[typing.Any]
    require_authentication: bool = True
    subresources: list[type['IResource']] = []
    verbose_name: str
    verbose_name_plural: str