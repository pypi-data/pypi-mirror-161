# Copyright (C) 2022 Cochise Ruhulessin <cochiseruhulessin@gmail.com>
# 
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
"""Declares :class:`NullCorsPolicy`."""
from typing import Any

import fastapi
import fastapi.params

from .basecorspolicy import BaseCorsPolicy


class NullCorsPolicy(BaseCorsPolicy):
    """Disable the CORS policy enforcement completely."""
    __module__: str = 'cbra.cors'
    origin_header: fastapi.params.Depends = fastapi.Depends(lambda: None)

    @classmethod
    def as_options(cls) -> 'ICorsPolicy': # type: ignore
        return cls()

    @classmethod
    def get_response_headers(cls) -> dict[str, Any]:
        return {}

    def __init__(self):
        pass

    async def get_allowed_origins(self) -> set[str]:
        return set()

    async def process_request(self, *args, **kwargs) -> None: # type: ignore
        pass

    async def process_response(self, *args, **kwargs) -> None: # type: ignore
        pass