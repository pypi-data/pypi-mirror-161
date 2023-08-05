# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`WebhookEndpoint`."""
import base64
import binascii
import urllib.parse
from typing import NoReturn
from typing import TypeAlias

from cbra.exceptions import WebhookMessageRejected
from cbra.ext import webhook
from cbra.ext.picqer.models import EventType
from cbra.parsers import JSONParser
from cbra.parsers import FormParser
from cbra.types import IParser
from .const import HEADER_DELIVERY_ID
from .const import HEADER_EVENT
from .const import HEADER_RESOURCE
from .const import HEADER_SIGNATURE
from .const import HEADER_SOURCE
from .const import HEADER_TOPIC
from .const import HEADER_WEBHOOK_ID
from .models import *


class WebhookEndpoint(webhook.WebhookEndpoint):
    """A :class:`cbra.ext.webhook.WebhookEndpoint` implementation
    that recognized incoming webhooks from WooCommerce (RESt API v3).
    """
    __module__: str = 'cbra.ext.woocommerce'
    allowed_events: set[str] = {"created", "updated", "deleted", "restored"}
    description: str = (
        "Receive a WooCommerce event and queue it for upstream "
        "processing.\n\n"
        "Refer to https://woocommerce.github.io/woocommerce-rest-api-docs "
        "for additional documentation on the WooCommerce v3 API."
    )
    echo: bool = False
    model: TypeAlias = EventType
    parsers: list[type[IParser]] = [
        JSONParser,
        FormParser
    ]
    summary: str = "WooCommerce (WP REST API integration v3)"
    wc_delivery_id: str | None
    wc_event: str | None
    wc_resource: str | None
    wc_signature: bytes | None
    wc_source: str | None
    wc_topic: str | None
    wc_webhook_id: str | None
    source: str | None = None

    def __init__(
        self,
        delivery_id: str | None = HEADER_DELIVERY_ID,
        event: str | None = HEADER_EVENT,
        resource: str | None = HEADER_RESOURCE,
        signature: str | None = HEADER_SIGNATURE,
        source: str | None = HEADER_SOURCE,
        topic: str | None = HEADER_TOPIC,
        webhook_id: str | None = HEADER_WEBHOOK_ID
    ):
        self.wc_delivery_id = delivery_id
        self.wc_event = event
        self.wc_resource = resource
        self.wc_source = source
        self.wc_signature = None
        self.wc_topic = topic
        self.wc_webhook_id = webhook_id
        if signature is not None:
            try:
                self.wc_signature = base64.b64decode(signature)
            except binascii.Error:
                raise WebhookMessageRejected(
                    message="The signature is malformed.",
                    detail=(
                        "The signature enclosed in the X-WC-Webhook-Signature "
                        "request header could not be interpreted as Base64."
                    )
                )
        if self.wc_source is not None:
            p = urllib.parse.urlparse(self.wc_source)
            self.source = p.netloc

    async def authenticate( # type: ignore
        self,
        dto: EventType
    ) -> NoReturn | None:
        """Verifies that the `X-WC-Signature` header was created using the
        preshared key.
        """
        if isinstance(dto, Ping):
            return
        await self.verify_request(
            signature=self.wc_signature or b'',
            secret=self.get_hmac_secret()
        )