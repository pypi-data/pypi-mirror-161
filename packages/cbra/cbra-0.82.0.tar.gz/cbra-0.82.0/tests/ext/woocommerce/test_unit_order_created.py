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


class TestOrderCreated(BaseMessageTest):
    event_type: str = 'created'
    resource_type: str = 'order'

    def get_request_params(self) -> dict[str, Any]:
        return {
            'headers': {
                'content-type': "application/json",
                'x-wc-webhook-delivery-id': "49b041fc9aee3f9aca0c0b5173c2b0d7",
                'x-wc-webhook-event': "created",
                'x-wc-webhook-id': "61",
                'x-wc-webhook-resource': "order",
                'x-wc-webhook-signature': "iuU91bAwFYjqebtl3dsJhJFR0Dst2VK2Yldz+Kf9VYk=",
                'x-wc-webhook-source': "https://test-wordpress.molano.nl/",
                'x-wc-webhook-topic': "order.created",
            },
            'content': (
                b'{"id":76,"parent_id":0,"status":"pending","currency":"EUR","version":"'
                b'5.9.1","prices_include_tax":false,"date_created":"2022-06-03T20:28:09"'
                b',"date_modified":"2022-06-03T20:28:58","discount_total":"0.00","discou'
                b'nt_tax":"0.00","shipping_total":"0.00","shipping_tax":"0.00","cart_tax'
                b'":"0.00","total":"0.00","total_tax":"0.00","customer_id":1,"order_key"'
                b':"wc_order_tpYsgYNGJe8OD","billing":{"first_name":"","last_name":"","c'
                b'ompany":"","address_1":"","address_2":"","city":"","state":"","postcod'
                b'e":"","country":"","email":"cochise.ruhulessin@unimatrixone.io","phone'
                b'":""},"shipping":{"first_name":"","last_name":"","company":"","address'
                b'_1":"","address_2":"","city":"","state":"","postcode":"","country":"",'
                b'"phone":""},"payment_method":"","payment_method_title":"","transaction'
                b'_id":"","customer_ip_address":"","customer_user_agent":"","created_via'
                b'":"admin","customer_note":"","date_completed":null,"date_paid":null,"c'
                b'art_hash":"","number":"76","meta_data":[],"line_items":[{"id":4,"name"'
                b':"Test Product p","product_id":39,"variation_id":0,"quantity":1,"tax_c'
                b'lass":"","subtotal":"0.00","subtotal_tax":"0.00","total":"0.00","total'
                b'_tax":"0.00","taxes":[],"meta_data":[],"sku":"XXXTEST","price":0,"pare'
                b'nt_name":null}],"tax_lines":[],"shipping_lines":[],"fee_lines":[],"cou'
                b'pon_lines":[],"refunds":[],"date_created_gmt":"2022-06-03T20:28:09","d'
                b'ate_modified_gmt":"2022-06-03T20:28:58","date_completed_gmt":null,"dat'
                b'e_paid_gmt":null,"currency_symbol":"\\u20ac","_links":{"self":[{"href":'
                b'"https:\\/\\/test-wordpress.molano.nl\\/wp-json\\/wc\\/v3\\/orders\\/76"}],"c'
                b'ollection":[{"href":"https:\\/\\/test-wordpress.molano.nl\\/wp-json\\/wc\\/'
                b'v3\\/orders"}],"customer":[{"href":"https:\\/\\/test-wordpress.molano.nl'
                b'\\/wp-json\\/wc\\/v3\\/customers\\/1"}]}}'
            )
        }