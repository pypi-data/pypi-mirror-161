# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`AortaEndpoint`."""
import asyncio
import warnings
from typing import Any
from typing import Awaitable

import aorta
import fastapi
from aorta.messagehandler import MessageHandler
from aorta.models import Message
from fastapi.dependencies.utils import get_parameterless_sub_dependant
from fastapi.dependencies.utils import solve_dependencies

from cbra import Endpoint
from cbra.exceptions import Unserializable
from cbra.transaction import Transaction
from cbra.transaction import NullTransaction
from .eventarcendpoint import EventarcEndpoint
from .models import PubsubMessage


class AortaEndpoint(EventarcEndpoint):
    __module__: str = 'cbra.ext.google'
    summary: str = "Aorta"
    description: str = (
        "Receive a `google.cloud.pubsub.topic.v1.messagePublished` message "
        "containing an Aorta command, event or task, and run all handlers."
        "\n\nThis endpoint may respond with a non-2xx response code if any "
        "of the handlers fails to process the message."
    )
    provider: aorta.MessageHandlersProvider = aorta.get_default_provider()
    transaction: Transaction = fastapi.Depends(NullTransaction)

    async def on_message(self, message: PubsubMessage) -> None | fastapi.Response:
        """Deserialize the Aorta object and run all matching handlers."""
        envelope = self.parse_aorta_message(message)
        handlers = self.provider.match(envelope) # type: ignore
        futures: list[Awaitable[None]] = []
        for handler_class in handlers:
            futures.append(self.run_handler(handler_class, envelope)) # type: ignore
        await asyncio.gather(*futures)

    async def run_handler(
        self,
        handler_class: type[MessageHandler],
        envelope: Message
    ) -> None:
        """Invoke `handler_class` with the given message."""
        obj: Any = envelope.get_object()
        dependant = get_parameterless_sub_dependant(
            depends=fastapi.Depends(handler_class),
            path='/'
        )
        values, errors, *_ = await solve_dependencies(
            request=self.request,
            dependant=dependant,
            body=obj,
            dependency_overrides_provider=None
        )
        if errors:
            warnings.warn(
                f"Improperly configured dependant: {handler_class.__name__}"
            )
            return
        handler: MessageHandler = dependant.call(**values) # type: ignore
        async with Transaction(publisher=self.publisher) as tx:
            tx.set_correlation_id(envelope.metadata.correlation_id)
            return await handler.handle(obj) # type: ignore

    def parse_aorta_message(self, message: PubsubMessage) -> Message:
        """Deserialize the message received from Google Pub/Sub and parse it
        into a previously registered Aorta type.
        """
        envelope: Message | None = None
        try:
            if not message.data or message.attributes:
                raise Unserializable
            envelope = self.provider.parse(message.get_data()) # type: ignore
        except Unserializable:
            warnings.warn(
                f"Message {message.message_id} did not contain an object "
                f"that was recognized by Aorta."
            )
            raise
        except aorta.UnknownMessageType:
            warnings.warn(
                f"Message {message.message_id} was succesfully deserialized "
                "but it did not contain an object that could be interpreted "
                "by Aorta."
            )
            raise

        self.logger.info(
            "Received %s/%s (id: %s, correlationId: %s)",
            envelope.api_version,
            envelope.kind,
            envelope.metadata.id,
            envelope.metadata.correlation_id
        )
        return envelope

    @Endpoint.register_exception # type: ignore
    async def on_unserializable(
        self,
        exception: Unserializable
    ) -> fastapi.Response:
        return fastapi.Response(
            status_code=200,
            headers={'X-Error-Code': "MALFORMED_OBJECT"}
        )

    @Endpoint.register_exception # type: ignore
    async def on_unknown_message_type(
        self,
        exception: aorta.exceptions.UnknownMessageType
    ) -> fastapi.Response:
        return fastapi.Response(
            status_code=200,
            headers={'X-Error-Code': "UNKNOWN_MESSAGE_TYPE"}
        )
