"""Declares :class:`ResourceOptions`."""
from inspect import Parameter
from typing import Any

from cbra.exceptions import get_exception_headers
from cbra.options import Options


class ResourceOptions(Options):
    is_detail: bool
    path_parameters: list[Parameter] = []

    @classmethod
    def get_path_signature(cls, detail: bool = False) -> list[Parameter]:
        return cls.path_parameters

    @classmethod
    def get_responses(cls) -> dict[int, Any]:
        responses = super().get_responses()
        if cls.is_detail:
            responses[404] = {
                'headers': get_exception_headers(404),
                'description': (
                    "The resource specified by the path parameter(s) does not exist."
                )
            }
        return responses