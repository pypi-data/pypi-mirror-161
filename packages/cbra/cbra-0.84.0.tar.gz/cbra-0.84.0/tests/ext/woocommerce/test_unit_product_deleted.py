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

from .basemessagetest import BaseMessageTest


class TestProductDelete(BaseMessageTest):
    event_type: str = 'deleted'
    resource_type: str = 'product'

    def get_request_params(self) -> dict[str, Any]:
        return {
            'headers': {
                'content-type': "application/json",
                'x-wc-webhook-delivery-id': "427d9a8e8269f1e7cbe7b26eacee4b4e",
                'x-wc-webhook-event': "deleted",
                'x-wc-webhook-id': "59",
                'x-wc-webhook-resource': "product",
                'x-wc-webhook-signature': "UYySC2m92uOtsOxltbamISzY3UU3Ns4DdlCm1HpEXyY=",
                'x-wc-webhook-source': "https://test-wordpress.molano.nl/",
                'x-wc-webhook-topic': "product.deleted",
            },
            'content': b'{"id":74}'
        }