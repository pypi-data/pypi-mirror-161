# pylint: skip-file
# type: ignore
import functools
import typing

from .basefiltermodel import BaseFilterModel
from .filteroption import FilterOption
from .iresource import IResource
from .publicresource import PublicResource
from .resource import Resource


__all__ = [
    'action',
    'BaseFilterModel',
    'FilterOption',
    'IResource',
    'PublicResource',
    'Resource'
]


def action(
    name: typing.Optional[str] = None,
    detail: bool = False,
    method: str = 'GET',
    path: typing.Optional[str] = None
) -> typing.Callable[..., typing.Any]:
    def action_factory(func):
        func.action = dict(
            name=name or func.__name__,
            method=method,
            is_detail=detail,
            subpath=path
        )
        return func
    return action_factory


def response(
    status_code: int = 200,
    summary: typing.Optional[str] = None
) -> typing.Any:
    """Decorate an action handler with the given properties."""
    pass