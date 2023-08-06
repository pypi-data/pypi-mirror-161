# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`EndpointMetaclass`."""
from typing import Any


class EndpointMetaclass(type):
    __module__: str = 'cbra'

    def __new__(
        cls,
        name: str,
        bases: tuple[type[object]],
        attrs: dict[str, Any]
    ):
        """Construct a new :class:`~cbra.Endpoint` class."""
        super_new = super().__new__
        if attrs.pop('__abstract__', False):
            return super_new(cls, name, bases, attrs)
        new_class = super_new(cls, name, bases, attrs)

        return new_class