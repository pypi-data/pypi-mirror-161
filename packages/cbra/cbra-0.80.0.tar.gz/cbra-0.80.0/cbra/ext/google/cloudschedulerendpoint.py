# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`CloudSchedulerEndpoint`."""
from typing import Any

from cbra.types import IContentNegotiation
from cbra.types import IRenderer
from cbra.utils import classproperty
from cbra.negotiation import NullContentNegotiation
from .googleendpoint import GoogleEndpoint


class CloudSchedulerEndpoint(GoogleEndpoint):
    """A :class:`~cbra.ext.google.GoogleEndpoint` implementation that handles
    a request that is received from Google Cloud Scheduler.
    """
    __module__: str = 'cbra.ext.google'
    negotiation: type[IContentNegotiation] = NullContentNegotiation
    default_response_code: int = 200
    renderers: list[type[IRenderer]] = []
    response_description: str = "The scheduled task completed succesfully."
    tags: list[str] = ["Cloud Scheduler"]

    @classproperty
    def responses(cls) -> dict[str | int, Any]:
        """The responses returned by this endpoint."""
        return {
            k: v for k, v in super().responses.items()
            if k in {400, 401, 403, 503, 'default'}
        }