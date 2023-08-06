# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`ICorsPolicy`."""
import typing
from typing import Any

import fastapi
import fastapi.params

from cbra.headers import ACCESS_CONTROL_REQUEST_HEADERS
from cbra.headers import ACCESS_CONTROL_REQUEST_METHOD
from cbra.headers import ORIGIN
from cbra.headers import CORS_HEADERS
from cbra.params import CurrentServer


class ICorsPolicy:
    __module__: str = 'cbra.types'
    allow_credentials: bool = False
    allowed_methods: set[str] = set()
    allowed_headers: set[str] = set()
    allowed_response_headers: set[str] = set()
    allowed_origins: set[str] = set()
    max_age: int = 86400
    origin: str | None
    origin_header: fastapi.params.Depends | fastapi.params.Header = ORIGIN # type: ignore
    request: fastapi.Request
    request_headers: set[str]
    request_methods: set[str]
    server: str
    OriginHeader: str | None = ORIGIN

    @classmethod
    def as_options(
        cls,
        request: fastapi.Request,
        server: str = CurrentServer,
        origin: str | None = ORIGIN,
        request_headers: typing.Optional[str] = ACCESS_CONTROL_REQUEST_HEADERS,
        request_methods: typing.Optional[str] = ACCESS_CONTROL_REQUEST_METHOD
    ) -> 'ICorsPolicy':
        instance = cls(
            request=request,
            server=server,
            origin=origin,
        )
        instance.request_headers = set(
            filter(bool, map(str.strip, str.split(request_headers or '', ',')))
        )
        instance.request_methods = set(
            filter(bool, map(str.strip, str.split(request_methods or '', ',')))
        )
        return instance

    @classmethod
    def configure(
        cls,
        *,
        allowed_headers: set[str] = set(),
        allowed_methods: set[str] = set()
    ) -> type['ICorsPolicy']:
        allowed_methods.add("OPTIONS")
        return type(cls.__name__, (cls,), {
            '__module__': cls.__module__,
            'allowed_headers': allowed_headers,
            'allowed_methods': allowed_methods
        })

    @classmethod
    def get_response_headers(cls) -> dict[str, Any]:
        return CORS_HEADERS

    def __init__(
        self,
        request: fastapi.Request,
        server: str = CurrentServer,
        origin: str | None = ORIGIN
    ):
        self.origin = origin
        self.request = request
        self.server = server

    async def add_response_headers(
        self,
        request: fastapi.Request,
        response: fastapi.Response,
        handler: typing.Any,
    ) -> None:
        raise NotImplementedError

    async def check_cors_allowed(
        self,
        handler: typing.Any,
        origin: typing.Optional[str]
    ) -> typing.Optional[typing.NoReturn]:
        raise NotImplementedError

    async def get_allowed_origins(self) -> set[str]:
        """Return the set of allowed origins."""
        raise NotImplementedError

    async def process_request(
        self,
        request: fastapi.Request,
        handler: typing.Any,
        origin: typing.Optional[str] = None
    ) -> typing.Union[bool, typing.NoReturn]:
        raise NotImplementedError

    async def process_response(
        self,
        request: fastapi.Request,
        response: fastapi.Response,
        handler: typing.Any,
        origin: typing.Optional[str] = None
    ) -> typing.Optional[typing.NoReturn]:
        raise NotImplementedError