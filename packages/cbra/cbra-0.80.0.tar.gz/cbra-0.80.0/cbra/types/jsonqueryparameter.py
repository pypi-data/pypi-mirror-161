"""Declares :class:`JSONQueryParameter`."""
import urllib.parse
from typing import Any
from typing import Generator


class JSONQueryParameter(str):

    @classmethod
    def __get_validators__(cls) -> Generator[Any, None, None]:
        yield cls.validate

    @classmethod
    def __modify_schema__(
        cls,
        field_schema: dict[str, Any]
    ) -> None: # pragma: no cover
        field_schema.update({
            "type": "str"
        })

    @classmethod
    def validate(
        cls,
        value: str | None
    ) -> "JSONQueryParameter":
        """Unquote the input data and deserialize as JSON."""
        if isinstance(value, cls) or value is None:
            return cls(value or '{}')
        return cls(urllib.parse.unquote(value))
        