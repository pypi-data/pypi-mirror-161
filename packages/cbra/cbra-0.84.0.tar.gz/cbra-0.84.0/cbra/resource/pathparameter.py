"""Declares :class:`PathParameter`."""
import inspect
import typing

import fastapi


class PathParameter:
    __module__: str = 'cbra.resource'
    name: str | None
    annotation: typing.Type[typing.Any]
    path_annotations: typing.Dict[typing.Any, typing.Any] = {
        'int': int,
        int: 'int',
    }
    signature_parameter: inspect.Parameter | None

    def __init__(
        self,
        name: typing.Optional[str],
        annotation: typing.Type[typing.Any]
    ):
        if name is not None and ':' in name:
            self.name, kind = str.split(name, ':')
            if kind not in self.path_annotations:
                raise ValueError(f"Unknown filter: '{kind}'.")
            self.annotation = self.path_annotations[kind]
        else:
            self.name = name
            self.annotation = str
            self.signature_parameter = None
        if self.name is not None:
            self.signature_parameter = inspect.Parameter(
                name=self.name,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=self.annotation,
                default=fastapi.Path(...)
            )

    def insert_in(self, seq: list[inspect.Parameter]) -> None:
        if self.signature_parameter is not None:
            seq.insert(0, self.signature_parameter)

    def get_path_variable(self) -> str:
        assert self.name is not None # nosec
        name = self.name
        if self.annotation != str:
            name = f'{name}:{self.path_annotations[self.annotation]}'
        return self.name

    def get_path(
        self,
        *,
        base_path: str,
        subpath: typing.Optional[str],
        is_detail: bool
    ) -> str:
        path = base_path
        if self.name is not None and is_detail:
            path = f'{path}/{{{self.get_path_variable()}}}'
        if subpath:
            path = f'{path}/{subpath}'
        return path

    def __bool__(self) -> bool:
        return self.name is not None

    def __eq__(self, other: object) -> bool:
        other = typing.cast(PathParameter, other)
        return self.name == other.name