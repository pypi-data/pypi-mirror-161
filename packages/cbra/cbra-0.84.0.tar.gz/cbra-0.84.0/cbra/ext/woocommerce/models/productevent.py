# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`ProductEvent`."""
import pydantic

from .event import Event
from .productstatustype import ProductStatusType
from .producttype import ProductType


class ProductEvent(Event):
    type: ProductType = pydantic.Field(
        default=...,
        title="Product type",
        description=(
            "Describes the type of product on which an event occurred."
        )
    )

    status: ProductStatusType = pydantic.Field(
        default=...,
        title="Status",
        description=(
            "The current status of the product resource."
        )
    )

    class Config:
        title: str = "WooCommerceProductEvent"