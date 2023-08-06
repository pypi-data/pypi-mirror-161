# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`EventarcEndpoint`."""
from typing import Any

from cbra.negotiation import NullResponseContentNegotiation
from cbra.parsers import JSONParser
from cbra.responses import EmptyResponse
from cbra.types import IContentNegotiation
from cbra.types import IParser
from cbra.types import IRenderer
from cbra.utils import classproperty
import fastapi
from .googleendpoint import GoogleEndpoint
from .models import MessagePublished
from .models import PubsubMessage


class EventarcEndpoint(GoogleEndpoint):
    """A :class:`~cbra.ext.google.GoogleEndpoint` implementation that handles
    messages pushed by Google Eventarc.
    """
    __module__: str = 'cbra.ext.google'
    response_class: type[EmptyResponse] = EmptyResponse
    default_response_code: int = 200
    model: type[MessagePublished] = MessagePublished
    negotiation: type[IContentNegotiation] = NullResponseContentNegotiation
    parsers: list[type[IParser]] = [JSONParser]
    renderers: list[type[IRenderer]] = []
    response_description: str = "The message is succesfully processed."
    summary: str = "Google Eventarc"
    tags: list[str] = ["Cloud Events"]

    @classproperty
    def responses(cls) -> dict[str | int, Any]:
        """The responses returned by this endpoint."""
        defaults = super().responses
        defaults.update({
            202: {
                'headers': cls.common_headers,
                'description': (
                    "The message processing or queued for processing."
                )
            }
        })
        return defaults

    async def handle(self, dto: MessagePublished) -> None | fastapi.Response: # type: ignore
        """Receive a `google.cloud.pubsub.topic.v1.messagePublished` message
        and invoke the appropriate handler.
        """
        self.logger.debug(
            "Received message %s from Google Pub/Sub",
            dto.message.message_id
        )
        return await self.on_message(dto.message)

    async def on_message(self, message: PubsubMessage) -> None | fastapi.Response:
        """Handles the message received from Google Pub/Sub. The default
        implementation raises a :exc:`NotImplementedError`.
        """
        raise NotImplementedError