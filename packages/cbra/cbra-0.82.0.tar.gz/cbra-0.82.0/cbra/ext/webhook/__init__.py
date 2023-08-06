# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Webhooks are an integral part of modern web applications. Many applications
consume external services through (REStful) APIs, and those services often
provide a mechanism to deliver event notifications to their consumers: webhooks.
The :mod:`cbra` framework provides a class-oriented solution to handle these
incoming messages.
"""
from typing import cast
from typing import Callable
from types import UnionType

import pydantic

from . import models
from .webhookendpoint import WebhookEndpoint


__all__ = [
    'models',
    'WebhookEndpoint'
]