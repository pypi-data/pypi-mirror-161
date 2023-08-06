# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`ResourceLinks`."""
import pydantic


class Link(pydantic.BaseModel):
    href: str


class ResourceLinks(pydantic.BaseModel):
    """Metadata describing the endpoints where the resource(s) can be
    retrieved.
    """
    self: list[Link]
    collection: list[Link]
