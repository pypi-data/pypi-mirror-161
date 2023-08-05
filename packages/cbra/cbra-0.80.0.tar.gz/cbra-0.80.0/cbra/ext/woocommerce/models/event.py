# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`Event`."""
import datetime

import pydantic

from .resourcelinks import ResourceLinks


class Event(pydantic.BaseModel):
    __module__: str = 'cbra.ext.woocommerce.models'

    id: int = pydantic.Field(
        default=...,
        title="ID",
        description=(
            "Identifies the resource on which an event occurred, in combination "
            "with the specified resource type in the `X-WC-Webhook-Resource` "
            "request header."
        )
    )

    date_created: datetime.datetime = pydantic.Field(
        default=...,
        title="Created",
        description=(
            "The date and time at which the object was created."
        )
    )

    date_created_gmt: datetime.datetime = pydantic.Field(
        default=...,
        title="Created (UTC)",
        description=(
            "The date and time at which the object was created (UTC)."
        )
    )

    date_modified: datetime.datetime = pydantic.Field(
        default=...,
        title="Modified",
        description=(
            "The date and time at which the object was last modified."
        )
    )

    date_modified_gmt: datetime.datetime = pydantic.Field(
        default=...,
        title="Modified (UTC)",
        description=(
            "The date and time at which the object was last modified (UTC)."
        )
    )

    links: ResourceLinks = pydantic.Field(
        default=...,
        alias="_links",
        title="Links"
    )

    def get_resource_uri(self) -> str:
        return self.links.self[0].href