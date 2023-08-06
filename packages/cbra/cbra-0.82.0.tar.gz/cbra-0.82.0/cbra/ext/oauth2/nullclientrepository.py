# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .types import IClient
from .types import IClientRepository


class NullClientRepository(IClientRepository):
    """A :class:`IClientRepository` implementation that has no clients."""

    async def exists(self, client_id: str) -> bool:
        return False

    async def get(self, client_id: str) -> IClient:
        raise self.ClientDoesNotExist