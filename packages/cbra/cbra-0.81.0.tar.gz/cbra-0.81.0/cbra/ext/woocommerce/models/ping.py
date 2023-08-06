# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`Ping`."""
import pydantic


class Ping(pydantic.BaseModel):
    __module__: str = 'cbra.ext.woocommerce.models'

    webhook_id: int = pydantic.Field(
        default=...,
        title="Webhook ID",
        description=(
            "The `id` attribute of the webhook that is being pinged "
            "by WooCommerce."
        )
    )

    class Config:
        title: str = "Ping"