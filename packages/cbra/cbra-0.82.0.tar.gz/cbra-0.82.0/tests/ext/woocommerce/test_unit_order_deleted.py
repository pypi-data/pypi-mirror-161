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


class TestOrderDeleted(BaseMessageTest):
    event_type: str = 'deleted'
    resource_type: str = 'order'

    def get_request_params(self) -> dict[str, Any]:
        return {
            'headers': {
                'content-type': "application/json",
                'x-wc-webhook-delivery-id': "b81aaee861e1ac036579255f2b61e495",
                'x-wc-webhook-event': "deleted",
                'x-wc-webhook-id': "63",
                'x-wc-webhook-resource': "order",
                'x-wc-webhook-signature': "FoPlvaJLF/h0tKiA6Xo6rw14pWwLQ84c+xrbByDKY7M=",
                'x-wc-webhook-source': "https://test-wordpress.molano.nl/",
                'x-wc-webhook-topic': "order.deleted",
            },
            'content': b'{"id":76}'
        }