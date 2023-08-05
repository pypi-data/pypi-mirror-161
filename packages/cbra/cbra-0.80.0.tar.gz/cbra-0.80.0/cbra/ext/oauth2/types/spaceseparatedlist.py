"""Declares :class:`SpaceSeparatedList`."""
import re
import typing


class SpaceSeparatedList(set[str]):
    __module__: str = 'cbra.ext.oauth2.types'
    sep: re.Pattern[str] = re.compile('\\s+')

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(
        cls,
        data: typing.Union[str, typing.List[str]]
    ) -> 'SpaceSeparatedList':
        if isinstance(data, (list, set)):
            return cls(data)
        return cls([x for x in cls.sep.split(data)]) if data else cls()

    @classmethod
    def __modify_schema__(
        cls,
        field_schema: typing.Dict[str, typing.Any]
    ):
        field_schema.update(
            type="string",
            example="value1 value2 value3"
        )

    def __repr__(self) -> str:
        return set(self).__repr__()

    def __str__(self) -> str:
        return str.join(' ', sorted(self))