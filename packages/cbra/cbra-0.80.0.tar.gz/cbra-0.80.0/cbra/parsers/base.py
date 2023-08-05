# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`BaseParser`."""
import abc
from typing import Any

import fastapi

from cbra.types import IParser


class BaseParser(IParser, metaclass=abc.ABCMeta):
    """All parsers should extend `BaseParser`, specifying a `media_type`
    attribute, and overriding the `.parse()` method.
    """
    media_type: str

    @classmethod
    def openapi_example(cls, schema: dict[str, Any]) -> str:
        return ""

    async def parse(
        self,
        request: fastapi.Request,
        media_type: str | None = None,
        parser_context: dict[str, Any] | None = None
    ) -> Any:
        """ Given a stream to read from, return the parsed representation.
        Should return parsed data, or a `DataAndFiles` object consisting of the
        parsed data and files.
        """
        raise NotImplementedError(".parse() must be overridden.")