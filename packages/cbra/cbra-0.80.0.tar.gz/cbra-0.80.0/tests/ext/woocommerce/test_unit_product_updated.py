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


class TestProductUpdated(BaseMessageTest):
    event_type: str = 'updated'
    resource_type: str = 'product'

    def get_request_params(self) -> dict[str, Any]:
        return {
            'headers': {
                'content-type': "application/json",
                'x-wc-webhook-delivery-id': "59edde97ec57fb8c05832b525fb27e9a",
                'x-wc-webhook-event': "updated",
                'x-wc-webhook-id': "57",
                'x-wc-webhook-resource': "product",
                'x-wc-webhook-signature': "oQ+wJoz5g/S9HJEwBIzVQYT1SQvlXJ3khoxeJbQroYo=",
                'x-wc-webhook-source': "https://test-wordpress.molano.nl/",
                'x-wc-webhook-topic': "product.updated"
            },
            'content': (
                b'{"id":57,"name":"variants 4 - foo, red","slug":"variants'
                b'-lijp-red-foo","permalink":"https:\/\/test-wordpress.mol'
                b'ano.nl\/product\/variants\/?attribute_teset=foo&attribut'
                b'e_color=red","date_created":"2022-05-03T13:39:45","date_'
                b'created_gmt":"2022-05-03T13:39:45","date_modified":"2022'
                b'-06-03T13:15:43","date_modified_gmt":"2022-06-03T13:15:4'
                b'3","type":"variation","status":"publish","featured":fals'
                b'e,"catalog_visibility":"visible","description":"<p>Tst<\/'
                b'p>\\n","short_description":"","sku":"XXXBAZ","price":"",'
                b'"regular_price":"","sale_price":"","date_on_sale_from":n'
                b'ull,"date_on_sale_from_gmt":null,"date_on_sale_to":null,'
                b'"date_on_sale_to_gmt":null,"on_sale":false,"purchasable"'
                b':false,"total_sales":"0","virtual":false,"downloadable":'
                b'false,"downloads":[],"download_limit":-1,"download_expir'
                b'y":-1,"external_url":"","button_text":"","tax_status":"t'
                b'axable","tax_class":"","manage_stock":true,"stock_quanti'
                b'ty":20,"backorders":"no","backorders_allowed":false,"bac'
                b'kordered":false,"low_stock_amount":null,"sold_individual'
                b'ly":false,"weight":"","dimensions":{"length":"","width":'
                b'"","height":""},"shipping_required":true,"shipping_taxab'
                b'le":true,"shipping_class":"","shipping_class_id":0,"revi'
                b'ews_allowed":false,"average_rating":"0.00","rating_count'
                b'":0,"upsell_ids":[],"cross_sell_ids":[],"parent_id":46,"'
                b'purchase_note":"","categories":[],"tags":[],"images":[],'
                b'"attributes":[{"id":0,"name":"teset","option":"foo"},{"i'
                b'd":0,"name":"color","option":"red"}],"default_attributes'
                b'":[],"variations":[],"grouped_products":[],"menu_order":'
                b'1,"price_html":"","related_ids":[],"meta_data":[],"stock'
                b'_status":"instock","_links":{"self":[{"href":"https:\/\/'
                b'test-wordpress.molano.nl\/wp-json\/wc\/v3\/products\/57"'
                b'}],"collection":[{"href":"https:\/\/test-wordpress.molan'
                b'o.nl\/wp-json\/wc\/v3\/products"}],"up":[{"href":"https:'
                b'\/\/test-wordpress.molano.nl\/wp-json\/wc\/v3\/products\/'
                b'46"}]}}'
            )
        }