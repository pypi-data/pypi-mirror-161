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


class TestProductRestored(BaseMessageTest):
    event_type: str = 'restored'
    resource_type: str = 'product'

    def get_request_params(self) -> dict[str, Any]:
        return {
            'headers': {
                'content-type': "application/json",
                'x-wc-webhook-delivery-id': "89d25cfbe5fb300cab823bb41ee020d9",
                'x-wc-webhook-event': "restored",
                'x-wc-webhook-id': "60",
                'x-wc-webhook-resource': "product",
                'x-wc-webhook-signature': "olvOF/mmu05Z4NmHGoJRg334+aKJRO+irbp/5OB4Ijc=",
                'x-wc-webhook-source': "https://test-wordpress.molano.nl/",
                'x-wc-webhook-topic': "product.restored",
            },
            'content': (
                b'{"id":74,"name":"product.created","slug":"product-cr'
                b'eated","permalink":"https:\/\/test-wordpress.molano.'
                b'nl\/product\/product-created\/","date_created":"2022'
                b'-06-03T17:22:45","date_created_gmt":"2022-06-03T17:2'
                b'2:45","date_modified":"2022-06-03T18:22:12","date_mo'
                b'dified_gmt":"2022-06-03T18:22:12","type":"simple","s'
                b'tatus":"publish","featured":false,"catalog_visibilit'
                b'y":"visible","description":"","short_description":""'
                b',"sku":"","price":"","regular_price":"","sale_price"'
                b':"","date_on_sale_from":null,"date_on_sale_from_gmt"'
                b':null,"date_on_sale_to":null,"date_on_sale_to_gmt":n'
                b'ull,"on_sale":false,"purchasable":false,"total_sales'
                b'":0,"virtual":false,"downloadable":false,"downloads"'
                b':[],"download_limit":-1,"download_expiry":-1,"extern'
                b'al_url":"","button_text":"","tax_status":"taxable","'
                b'tax_class":"","manage_stock":false,"stock_quantity":'
                b'null,"backorders":"no","backorders_allowed":false,"b'
                b'ackordered":false,"low_stock_amount":null,"sold_indi'
                b'vidually":false,"weight":"","dimensions":{"length":"'
                b'","width":"","height":""},"shipping_required":true,"'
                b'shipping_taxable":true,"shipping_class":"","shipping'
                b'_class_id":0,"reviews_allowed":true,"average_rating"'
                b':"0.00","rating_count":0,"upsell_ids":[],"cross_sell'
                b'_ids":[],"parent_id":0,"purchase_note":"","categorie'
                b's":[{"id":15,"name":"Uncategorized","slug":"uncatego'
                b'rized"}],"tags":[],"images":[],"attributes":[],"defa'
                b'ult_attributes":[],"variations":[],"grouped_products'
                b'":[],"menu_order":0,"price_html":"","related_ids":[4'
                b'6,44,13,39,14],"meta_data":[],"stock_status":"instoc'
                b'k","_links":{"self":[{"href":"https:\/\/test-wordpre'
                b'ss.molano.nl\/wp-json\/wc\/v3\/products\/74"}],"coll'
                b'ection":[{"href":"https:\/\/test-wordpress.molano.nl'
                b'\/wp-json\/wc\/v3\/products"}]}}'
            )
        }