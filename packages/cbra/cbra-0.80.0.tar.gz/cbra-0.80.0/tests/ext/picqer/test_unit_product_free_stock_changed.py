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


class TestProductFreeStockChanged(BaseMessageTest):

    def get_request_params(self) -> dict[str, Any]:
        return {
            'headers': {
                'content-type': 'application/json',
                self.signature_header: "xmH72hlRe4aSLrI9eVAMOdbr8i7zdDoLkwg7Pl2E+3k="
            },
            'content': (
                b'{"idhook":12389,"name":"log-request-products-free_stock_changed","even'
                b't":"products.free_stock_changed","event_triggered_at":"2022-06-04 10:3'
                b'7:55","data":{"idproduct":19567274,"idvatgroup":13478,"idsupplier":nul'
                b'l,"productcode":"XXXTEST","name":"Test Product","price":0.08,"fixedsto'
                b'ckprice":0,"productcode_supplier":"","deliverytime":0,"description":"T'
                b'estproduct voor API- en systeemintegraties. Bestaat niet.","barcode":"'
                b'","unlimitedstock":false,"assembled":false,"type":"normal","weight":0,'
                b'"length":null,"width":null,"height":null,"minimum_purchase_quantity":0'
                b',"purchase_in_quantities_of":0,"hs_code":"","country_of_origin":"","ac'
                b'tive":true,"comment_count":0,"analysis_abc_classification":null,"analy'
                b'sis_pick_amount_per_day":null,"tags":{},"productfields":[{"idproductfi'
                b'eld":2603,"title":"Mapping 1: Categorie","value":"iPhone"},{"idproduct'
                b'field":2604,"title":"Mapping 2: Grading level","value":"ABC"},{"idprod'
                b'uctfield":2605,"title":"Mapping 3: Grade \/ Functionality","value":"A"'
                b'},{"idproductfield":2606,"title":"Mapping 5: Body Grade","value":"-"},'
                b'{"idproductfield":2607,"title":"Mapping 4: Screen Grade","value":"-"},'
                b'{"idproductfield":2608,"title":"Mapping 6: Device","value":"iPhone Izz'
                b'y"},{"idproductfield":2609,"title":"Mapping 7: Storage","value":"X"},{'
                b'"idproductfield":2610,"title":"Mapping 8: Release Year","value":"X"},{'
                b'"idproductfield":2611,"title":"Mapping 9: Macbook Inch","value":"X"},{'
                b'"idproductfield":2612,"title":"Mapping. 10: Parts Cat.","value":"X"},{'
                b'"idproductfield":2613,"title":"Mapping. 11: Accessoires Cat.","value":'
                b'"X"},{"idproductfield":2688,"title":"Mapping. 12: VAT","value":"VAT"},'
                b'{"idproductfield":2690,"title":"Mapping. 13: Colour","value":"-"}],"im'
                b'ages":[],"stock":[{"idwarehouse":6790,"stock":1,"reserved":1,"reserved'
                b'backorders":1,"reservedpicklists":0,"reservedallocations":0,"freestock'
                b'":0}],"pricelists":[]}}'
            )
        }