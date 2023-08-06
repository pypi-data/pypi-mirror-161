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


class TestProductCreated(BaseMessageTest):
    event_type: str = 'created'
    resource_type: str = 'product'

    def get_request_params(self) -> dict[str, Any]:
        return {
            'headers': {
                'content-type': "application/json",
                'x-wc-webhook-delivery-id': "4df0a951a314adc554e0f2016102e020",
                'x-wc-webhook-event': "created",
                'x-wc-webhook-id': "58",
                'x-wc-webhook-resource': "product",
                'x-wc-webhook-signature': "xDHr5XRGdiaAVKotCrxsHHfLXWaO+MzXOmBVKs1uNWQ=",
                'x-wc-webhook-source': "https://test-wordpress.molano.nl/",
                'x-wc-webhook-topic': "product.created",
            },
            'content': (
                b'{"id":74,"name":"product.created","slug":"product-create'
                b'd","permalink":"https:\\/\\/test-wordpress.molano.nl\\/prod'
                b'uct\\/product-created\\/","date_created":"2022-06-03T17:22'
                b':45","date_created_gmt":"2022-06-03T17:22:45","date_modi'
                b'fied":"2022-06-03T17:22:45","date_modified_gmt":"2022-06'
                b'-03T17:22:45","type":"simple","status":"publish","featur'
                b'ed":false,"catalog_visibility":"visible","description":"'
                b'","short_description":"","sku":"","price":"","regular_pr'
                b'ice":"","sale_price":"","date_on_sale_from":null,"date_o'
                b'n_sale_from_gmt":null,"date_on_sale_to":null,"date_on_sa'
                b'le_to_gmt":null,"on_sale":false,"purchasable":false,"tot'
                b'al_sales":0,"virtual":false,"downloadable":false,"downlo'
                b'ads":[],"download_limit":-1,"download_expiry":-1,"extern'
                b'al_url":"","button_text":"","tax_status":"taxable","tax_'
                b'class":"","manage_stock":false,"stock_quantity":null,"ba'
                b'ckorders":"no","backorders_allowed":false,"backordered":'
                b'false,"low_stock_amount":null,"sold_individually":false,'
                b'"weight":"","dimensions":{"length":"","width":"","height'
                b'":""},"shipping_required":true,"shipping_taxable":true,"'
                b'shipping_class":"","shipping_class_id":0,"reviews_allowe'
                b'd":true,"average_rating":"0.00","rating_count":0,"upsell'
                b'_ids":[],"cross_sell_ids":[],"parent_id":0,"purchase_not'
                b'e":"","categories":[{"id":15,"name":"Uncategorized","slu'
                b'g":"uncategorized"}],"tags":[],"images":[],"attributes":'
                b'[],"default_attributes":[],"variations":[],"grouped_prod'
                b'ucts":[],"menu_order":0,"price_html":"","related_ids":[3'
                b'9,46,14,44,13],"meta_data":[],"stock_status":"instock","'
                b'_links":{"self":[{"href":"https:\\/\\/test-wordpress.molan'
                b'o.nl\\/wp-json\\/wc\\/v3\\/products\\/74"}],"collection":[{"h'
                b'ref":"https:\\/\\/test-wordpress.molano.nl\\/wp-json\\/wc\\/v'
                b'3\\/products"}]}}'
            )
        }