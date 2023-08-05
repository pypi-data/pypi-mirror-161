# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`DebugTransport`."""
import asyncio
import base64
import datetime
import os
from typing import Awaitable

import aorta
import aorta.models
from httpx import AsyncClient

import cbra
from .models import MessagePublished
from .models import PubsubMessage


class DebugTransport(aorta.transport.ITransport): # pragma: no cover
    """A :class:`aorta.transport.ITransport` implementation that sends
    messages to the ASGI application provided to the constructor.
    """

    def __init__(self, app: cbra.Application, base_url: str, path: str):
        self.app = app
        self.base_url = base_url
        self.path = path

    async def send(self, objects: list[aorta.models.MessageHeader]):
        """Construct a :class:`~cbra.ext.google.models.MessagePublished`
        instance and send it to the Eventarc endpoint.
        """
        futures: list[Awaitable[None]] = []
        async with AsyncClient(app=self.app, base_url=self.base_url) as client:
            for obj in objects:
                message = MessagePublished(
                    subscription="projects/abcdef/subscriptions/abcdef",
                    message=PubsubMessage(
                        messageId=bytes.hex(os.urandom(16)),
                        publishTime=datetime.datetime.utcnow(),
                        attributes={},
                        data=bytes.decode(base64.b64encode(bytes(obj)))
                    )
                )
                futures.append(self._send(client, message))

            await asyncio.gather(*futures)

    async def _send(self, client: AsyncClient, message: MessagePublished):
        response = await client.post( # type: ignore
            url=self.path,
            data=message.json(by_alias=True), # type: ignore
            headers={
                'Accept': "application/json",
                'Content-Type': "application/json"
            }
        )
        if response.status_code not in {200, 202}:
            raise Exception(response.text, response.status_code, response.url)
