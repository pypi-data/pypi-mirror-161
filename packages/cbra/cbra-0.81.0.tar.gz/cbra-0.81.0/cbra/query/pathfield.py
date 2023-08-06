"""Declares :class:`Path`."""
import pydantic.fields


class PathField(pydantic.fields.FieldInfo):
    """A :class:`pydantic.Field` implementation that indicates that
    a parameter comes from the request path component.
    """
    pass
