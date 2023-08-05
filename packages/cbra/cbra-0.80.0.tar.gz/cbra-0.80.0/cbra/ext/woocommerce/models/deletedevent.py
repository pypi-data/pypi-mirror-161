# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`DeletedEvent`."""
import pydantic


class DeleteEvent(pydantic.BaseModel):
    id: int = pydantic.Field(
        default=...,
        title="ID",
        description=(
            "The identifier of the object that was deleted. Use "
            "the `X-WC-Resource` header to determine the actual "
            "type of the resource."
        )
    )

    class Config:
        title: str = "WooCommerceDeleteEvent"