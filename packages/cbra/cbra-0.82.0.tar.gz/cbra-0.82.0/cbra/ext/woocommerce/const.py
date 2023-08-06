# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi


HEADER_DELIVERY_ID: str = fastapi.Header(
    default=None,
    alias='X-WC-Webhook-Delivery-ID',
    title="Delivery ID",
    description=(
        "An identifier for this specific delivery. Use this value to lookup "
        "the delivery in the WooCommerce logs."
    )
)

HEADER_EVENT: str = fastapi.Header(
    default=None,
    alias='X-WC-Webhook-Event',
    title="Event",
    description=(
        "The event that occurred on the resource specified by the "
        "`X-WC-Webhook-Resource`, e.g. 'created', 'updated' or 'deleted'. "
    )
)

HEADER_SIGNATURE: str = fastapi.Header(
    default=None,
    alias='X-WC-Webhook-Signature',
    title="Signature",
    description=(
        "A Hash-based Message Authenticated Code (HMAC) calculated from "
        "the request body, using a previously shared key between "
        "the server and the WooCommerce instance. The signature is encoded "
        "using the Base64 encoding."
    )
)

HEADER_SOURCE: str  = fastapi.Header(
    default=None,
    alias="X-WC-Webhook-Source",
    title="Source",
    description=(
        "A URL specifing the source WooCommerce instance."
    )
)

HEADER_TOPIC: str = fastapi.Header(
    default=None,
    alias="X-WC-Webhook-Topic",
    title="Topic",
    description=(
        "The topic of the event, e.g. `order.updated`."
    )
)

HEADER_RESOURCE: str = fastapi.Header(
    default=None,
    alias="X-WC-Webhook-Resource",
    title="Resource",
    description=(
        "The kind of resource on which an event occurred."
    ),
    enum=['coupon', 'customer', 'order', 'product']
)

HEADER_WEBHOOK_ID: str = fastapi.Header(
    default=None,
    alias='X-WC-Webhook-ID',
    title="Webhook ID",
    description=(
        "Identifies the webhook that sent the event."
    )
)