"""Declares :class:`FilterOption`."""
from typing import Any

import fastapi
import fastapi.params


class FilterOption:
    """Declares a query parameter that may be used to apply a filtering
    criterion to the collection endpoint.
    """
    __module__: str = 'cbra.resource'
    alias: str
    attname: str
    description: str
    annotation: type[Any]
    title: str | None
    default: type[Any] | None = None

    def __init__(
        self,
        *,
        alias: str,
        description: str,
        title: str | None = None,
        annotation: type[Any] = str,
        attname: str | None = None,
        default: Any | None = None
    ):
        self.alias = alias
        self.attname = attname or alias
        self.description = description
        self.annotation = annotation
        self.title = title
        self.default = default

    def add_to_namespace(self, attrs: dict[str, Any]) -> None:
        """Add the :class:`FilterOption` instance to the namespace
        (attributes) for a class, prior to constructing it during
        type initialization.
        """
        annotations = attrs.setdefault('__annotations__', {})
        annotations[self.attname] = self.annotation
        attrs[self.attname] = self.as_query()

    def as_query(self) -> fastapi.params.Query:
        """Return the :class:`FilterOption` as an instance of
        :class:`fastapi.params.Query`.
        """
        return fastapi.Query(
            alias=self.alias,
            default=self.default,
            title=self.title or str.title(self.alias),
            description=self.description,
        )