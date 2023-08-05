# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`MoneybirdWebhook`."""
from typing import TypeAlias

from cbra.ext import webhook
from .models import EventType


class MoneybirdWebhook(webhook.WebhookEndpoint):
    __module__: str = 'cbra.ext.moneybird'
    summary: str = "Moneybird"
    model: TypeAlias = EventType
    description: str = (
        "Receive a Moneybird event and queue it for upstream "
        "processing.\n\n"
        "Refer to https://developer.moneybird.com for additional "
        "documentation on the Moneybird API."
    )