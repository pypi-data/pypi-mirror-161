"""Declares :class:`StringOrList`."""
import typing


class StringOrList(set):
    __module__: str = 'cbra.ext.oauth2'

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(
        cls,
        data: typing.Union[str, typing.List[set]]
    ):
        if isinstance(data, str):
            data = [data]
        return set(sorted(data or []))

    @classmethod
    def __modify_schema__(
        cls,
        field_schema: typing.Dict[str, typing.Any]
    ) -> None:
        field_schema.update(
            type="array",
            items={"type": "string"}
        )