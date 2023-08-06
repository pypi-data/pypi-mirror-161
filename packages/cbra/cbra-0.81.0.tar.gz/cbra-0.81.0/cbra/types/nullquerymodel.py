"""Declares :class:`NullQueryModel`."""
from pydantic import dataclasses

from .basequerymodel import BaseQueryModel


@dataclasses.dataclass
class NullQueryModel(BaseQueryModel):
    """The default query model for endpoints that have no query parameters."""