# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`IParser`."""
from typing import Any

from .request import Request


class IParser:
    __module__: str = 'cbra.types'
    encoding: str | None
    media_type: str

    @classmethod
    def openapi_example(cls, schema: dict[str, Any]) -> str:
        return ""

    def __init__(self,
        encoding: str | None = None
    ):
        self.encoding = encoding

    async def parse(self,
        request: Request,
        media_type: str | None = None,
        parser_context: dict[str, Any] | None = None
    ) -> Any:
        raise NotImplementedError