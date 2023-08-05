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
import hmac
import warnings
from typing import Any
from typing import NoReturn

from cbra.cors import NullCorsPolicy
from cbra.endpoint import Endpoint
from cbra.exceptions import WebhookMessageRejected
from cbra.types import ICorsPolicy
from cbra.utils import DeferredException
from .models import WebhookResponse
from .webhookendpointmetaclass import WebhookEndpointMetaclass


class WebhookEndpoint(Endpoint, metaclass=WebhookEndpointMetaclass):
    """A :class:`~cbra.Endpoint` implementation that provides a base to
    implement incoming webhook handlers.
    """
    __module__: str = 'cbra.ext.webhook'
    cors_policy: type[ICorsPolicy] = NullCorsPolicy
    method: str = "POST"
    tags: list[str] = ["Webhooks"]
    summary: str = "Webhook events endpoint"
    response_description: str = "The event is accepted for upstream processing."
    response_model: type[WebhookResponse] = WebhookResponse

    @classmethod
    async def create_webhooks(
        cls,
        *,
        hooks: list[dict[str, Any]],
        secret: str,
        **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Take a list of webhook definitions and ensure that they are present
        at the remote system. Return the list of definitions, enriched with data
        returned from the remote system, if any.
        """
        raise NotImplementedError

    def decode_signature(self, signature: str) -> bytes | DeferredException:
        """Decode a Base64-encoded string containing a signature of the request
        payload.
        """
        try:
            return base64.b64decode(signature)
        except (binascii.Error, TypeError, ValueError):
            return WebhookMessageRejected.defer(
                message="The signature is malformed.",
                detail=(
                    "The signature enclosed in the X-WC-Webhook-Signature "
                    "request header could not be interpreted as Base64."
                )
            )

    def get_hmac_secret(self) -> bytes:
        """Return a byte-sequence containing the secret used to verify
        the Hash-based Message Authenticate Code (HMAC) that WooCommerce
        creates in order to secure the request.
        """
        raise NotImplementedError

    async def handle( # type: ignore
        self,
        dto: Any
    ) -> WebhookResponse:
        on_event = getattr(self, 'on_event', self.sink)
        try:
            result = await on_event(dto) or {'status': 'accepted'}
        except Exception as exception:
            self.logger.exception(
                "Caught fatal %s while handling webhook event",
                type(exception).__name__
            )
            result = {'status': 'failed'}
        return WebhookResponse(**result)

    def log_event(self, dto: Any) -> None:
        """Logs the incoming webhook event. This method must be overridden
        as the default implementation raises :exc:`NotImplementedError`.
        """
        raise NotImplementedError

    async def sink(self, dto: Any) -> dict[str, Any]:
        """Invoked for webhook events that do not have any defined
        handlers.
        """
        warnings.warn(f'No handler for event {type(dto).__name__}')
        return {'status': 'dropped'}

    async def verify_request(
        self,
        signature: bytes,
        secret: bytes
    ) -> NoReturn | None:
        """Verifies that a SHA-256 digest of the request body was used to
        create a Hash-based Message Authentication Code (HMAC) using
        `secret`.
        """
        try:
            is_valid = hmac.compare_digest(
                hmac.digest(secret, await self.request.body(), 'sha256'),
                bytes(signature)
            )
        except (TypeError, ValueError): # pragma: no cover
            is_valid = False
        if not is_valid:
            raise WebhookMessageRejected(
                message="The request signature is not valid.",
                detail=(
                    "The signature provided attached to the request "
                    "did not validate against a HMAC-SHA256 comparison "
                    "using the pre-shared secret."
                )
            )