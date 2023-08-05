# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# type: ignore
"""Declares :class:`WebhookEndpointMetaclass`."""
import copy
from collections import OrderedDict
from inspect import signature
from inspect import Parameter
from typing import cast
from typing import Any

from cbra import Endpoint
from cbra import EndpointMetaclass
from .models import WebhookResponse


class WebhookEndpointMetaclass(EndpointMetaclass):
    __module__: str = 'cbra.ext.webhook'

    def __new__(
        cls,
        name: str,
        bases: tuple[type[object]],
        attrs: dict[str, Any]
    ):
        Base = cast(
            type[Endpoint],
            super().__new__(cls, name, bases, attrs)
        )
        if Base.model is None or attrs.pop('__concrete__', False):
            return Base

        # Create a new class with the proper annotation
        class WebhookEndpoint(Base):
            __concrete__: bool = True

            async def handle(self, dto: Base.model) -> WebhookResponse:
                return await super().handle(dto)

        return WebhookEndpoint