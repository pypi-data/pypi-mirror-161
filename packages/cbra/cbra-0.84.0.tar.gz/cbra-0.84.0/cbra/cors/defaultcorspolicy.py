"""Declares :class:`DefaultPolicy`."""
from typing import Any

from .basecorspolicy import BaseCorsPolicy


class DefaultPolicy(BaseCorsPolicy):
    __module__: str = 'cbra.cors'

    @classmethod
    def new(cls, **attrs: Any) -> type['DefaultPolicy']:
        return type(cls.__name__, (cls,), attrs)