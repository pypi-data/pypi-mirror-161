# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from unimatrix.conf import settings # type: ignore

from .models import DependencyList
from .provider import _default # type: ignore


DEPENDENCIES: list[Any] = getattr(
    settings, 'DEPENDENCIES', [] # type: ignore
)


async def init():
    """Loads the preconfigured dependencies in the default provider."""
    await _default.load_many(DependencyList(items=DEPENDENCIES))