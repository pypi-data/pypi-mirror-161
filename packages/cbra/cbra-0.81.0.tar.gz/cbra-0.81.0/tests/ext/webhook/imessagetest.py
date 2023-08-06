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
import base64
import json
from typing import Any

import pytest
from httpx import AsyncClient


class IMessageTest:
    event_type: str
    resource_type: str
    signature_header: str

    def get_request_params(self) -> dict[str, Any]:
        raise NotImplementedError

    def test_content_is_json_parseable(self) -> None:
        params = self.get_request_params()
        json.loads(bytes.decode(params['content']))

    @pytest.mark.asyncio
    async def test_accept_event(
        self,
        client: AsyncClient
    ) -> None:
        raise NotImplementedError

    @pytest.mark.asyncio
    async def test_disallowed_event_is_rejected(
        self,
        client: AsyncClient
    ) -> None:
        pytest.skip()

    @pytest.mark.asyncio
    async def test_missing_signature(
        self,
        client: AsyncClient
    ) -> None:
        params = self.get_request_params()
        self.remove_signature_header(params)
        response = await client.post(url='/', **params) # type: ignore
        dto = response.json()
        assert response.status_code == 403, response.text
        assert dto['spec']['code'] == 'WEBHOOK_EVENT_REJECTED'
        assert dto['spec']['message'] == "The request signature is not valid."

    @pytest.mark.asyncio
    async def test_malformed_signature(
        self,
        client: AsyncClient
    ) -> None:
        params = self.get_request_params()
        self.add_malformed_signature(params)
        response = await client.post(url='/', **params) # type: ignore
        dto = response.json()
        assert response.status_code == 403, response.text
        assert dto['spec']['code'] == 'WEBHOOK_EVENT_REJECTED'
        assert dto['spec']['message'] == "The signature is malformed."

    @pytest.mark.asyncio
    async def test_mismatching_signature(
        self,
        client: AsyncClient
    ) -> None:
        params = self.get_request_params()
        self.add_mismatching_signature(params)
        response = await client.post(url='/', **params) # type: ignore
        dto = response.json()
        assert response.status_code == 403, response.text
        assert dto['spec']['code'] == 'WEBHOOK_EVENT_REJECTED'
        assert dto['spec']['message'] == "The request signature is not valid."

    def add_malformed_signature(self, params: dict[str, Any]) -> dict[str, Any]:
        params['headers'][self.signature_header] = 'foo'

    def add_mismatching_signature(self, params: dict[str, Any]) -> dict[str, Any]:
        params['headers'][self.signature_header] = base64.b64encode(b'foo')

    def remove_signature_header(self, params: dict[str, Any]) -> dict[str, Any]:
        del params['headers'][self.signature_header]