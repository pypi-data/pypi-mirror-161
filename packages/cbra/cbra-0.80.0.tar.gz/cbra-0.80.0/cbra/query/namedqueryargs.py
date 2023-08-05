"""Declares :class:`NamedQueryArgs`."""
import pydantic


class NamedQueryArgs(pydantic.BaseModel):
    """A :class:`pydantic.BaseModel` implementation that provides some hooks
    for the :class:`cbra.QueryRunner` to execute the query.
    """
