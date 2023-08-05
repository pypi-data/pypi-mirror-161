# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`WebhookEndpoint`."""
import asyncio
import functools
import warnings
from typing import cast
from typing import Any
from typing import Awaitable
from typing import NoReturn
from typing import TypeAlias

import fastapi
import pydantic
from httpx import AsyncClient
from httpx import BasicAuth

from cbra.ext import webhook
from cbra.parsers import JSONParser
from cbra.types import IParser
from . import models


class WebhookEndpoint(webhook.WebhookEndpoint):
    __module__: str = 'cbra.ext.picqer'
    description: str = (
        "Receive a Picqer event and queue it for upstream "
        "processing.\n\n"
        "Refer to https://picqer.com/en/api for additional "
        "documentation on the Picqer API."
    )
    model: TypeAlias = models.EventType
    parsers: list[type[IParser]] = [JSONParser]
    summary: str = "Picqer"
    signature: bytes | None = None

    @classmethod
    async def create_webhooks(
        cls,
        *,
        hooks: list[dict[str, Any]],
        secret: str,
        base_url: str,
        email: str,
        api_key: str,
        **kwargs: Any
    ) -> list[dict[str, Any]]: # pragma: no cover
        """Ensure that the given list of webhooks `hooks` exists at the
        Picqer instance identified by `base_url`.
        """
        params = {
            'auth': BasicAuth(username=api_key, password='x'),
            'base_url': base_url,
            'headers': {
                'User-Agent': f"MyPicqerClient (picqer.com/api - {email})"
            }
        }
        futures: list[Awaitable[dict[str, Any]]] = []
        async with AsyncClient(**params) as client:
            for hook in hooks:
                futures.append(
                    cls._get_or_create_webhook(client, hook, secret)
                )
            await asyncio.gather(*futures)

        return hooks

    @staticmethod
    async def _get_or_create_webhook(
        client: AsyncClient,
        hook: dict[str, Any],
        secret: str
    ) -> dict[str, Any]: # pragma: no cover
        response = await client.post( # type: ignore
            url='/api/v1/hooks',
            json=hook
        )
        if response.status_code not in {201, 400}:
            response.raise_for_status()
        if response.status_code == 400:
            dto = response.json()
            if dto.get('error_message') != "Error: Hook already exists":
                response.raise_for_status()
        if response.status_code == 201:
            remote = response.json()
            hook['idhook'] = remote['idhook']
        return hook

    def __init__(
        self,
        signature: str | None = fastapi.Header(
            default=None,
            title="Signature",
            alias='X-Picqer-Signature',
            description=(
                "A Base64-encoded Hash-based Message Authentication Code (HMAC) "
                "of the request body, that was created using a pre-shared secret."
            )
        )
    ):
        if signature is not None:
            self.signature = cast(bytes, self.decode_signature(signature))

    async def authenticate( # type: ignore
        self,
        dto: models.EventType
    ) -> NoReturn | None:
        """Verifies that the `X-WC-Signature` header was created using the
        preshared key.
        """
        await self.verify_request(
            signature=self.signature or b'',
            secret=self.get_hmac_secret()
        )

    @functools.singledispatchmethod
    async def get_object(
        self,
        dto: models.EventType
    ) -> dict[str, Any] | pydantic.BaseModel:
        """Return the object on which the event occurred."""
        raise NotImplementedError

    @functools.singledispatchmethod
    async def on_event(
        self,
        dto: models.EventType
    ) -> dict[str, Any] | None: # pragma: no cover
        """Handles the incoming event message or emit a warning if there is
        no handler defined.
        """
        return await self.sink(dto)

    @on_event.register
    async def on_order_closed(
        self,
        dto: models.OrderClosed
    ) -> dict[str, Any] | None:
        """Invoked when an ``orders.closed`` event is received."""
        return await self.sink(dto)

    @on_event.register
    async def on_free_stock_changed(
        self,
        dto: models.ProductFreeStockChanged
    ) -> dict[str, Any] | None:
        """Invoked when a ``products.free_stock_changed`` event is received."""
        return await self.sink(dto)

    async def sink(self, dto: models.EventType, **params: Any) -> dict[str, Any]:
        warnings.warn(
            f"{type(self).__name__} did not specify a handler method for "
            f"event type {dto.event} ({type(dto).__name__})"
        )
        return {
            'status': 'dropped',
            **params
        }