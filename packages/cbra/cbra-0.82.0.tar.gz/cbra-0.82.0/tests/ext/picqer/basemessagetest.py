# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# pylint: skip-file
# type: ignore
from typing import Any

import pytest
from httpx import AsyncClient

from ..webhook.imessagetest import IMessageTest


class BaseMessageTest(IMessageTest):
    signature_header: str = 'x-picqer-signature'

    @pytest.mark.asyncio
    async def test_accept_event(
        self,
        client: AsyncClient
    ) -> None:
        params = self.get_request_params()
        response = await client.post(url='/', **params) # type: ignore
        dto = response.json()
        assert response.status_code == 200, response.text