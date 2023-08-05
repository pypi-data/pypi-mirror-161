import time

from dataclasses import dataclass
from typing import List, Dict

from purchase.utils import repeatable_request
from purchase.strings.verifiers import APPLE_URL, APPLE_SANDBOX_URL, APPLE_HEADERS


@dataclass
class AppleVerifier:
    receipt: dict
    is_sandbox: bool
    product_id: str
    platform: str
    version: str
    transaction_id: str
    is_sub: bool = False

    def get_url(self):
        if self.is_sandbox:
            return APPLE_SANDBOX_URL
        return APPLE_URL

    def verify(self) -> (bool, bool):
        data = {"receipt-data": self.receipt["payload"]}
        url = self.get_url()
        is_sandbox, result = self.request(url, data)
        return is_sandbox, result

    def get_pos(self, products: List[Dict]) -> int:
        pos = [
            ind
            for ind, product in enumerate(products)
            if product.get("product_id") == self.product_id
            and product.get("transaction_id") == self.transaction_id
        ]
        if len(pos):
            return pos[0]
        pos = [
            ind
            for ind, product in enumerate(products)
            if product.get("original_transaction_id") == self.transaction_id
        ]
        return pos[0]

    def products_is_ok(self, products: List[Dict]) -> bool:
        contains = (
            any(
                True
                for product in products
                if product.get("product_id") == self.product_id
                and product.get("transaction_id") == self.transaction_id
            ),
            any(
                True
                for product in products
                if product.get("original_transaction_id") == self.transaction_id
            )
        )
        if not self.is_sub:
            return any(contains)
        pos = self.get_pos(products)
        product = products[pos]
        exp = product.get("expires_date_ms")
        now = round(time.time() * 1000)
        return now < exp

    def request(self, url: str, data: dict) -> (bool, bool):
        is_sandbox = self.is_sandbox
        result = False

        response = repeatable_request(url=url, json=data, headers=APPLE_HEADERS).json()

        if response["status"] == 21008:  # is not sandbox
            is_sandbox = False
            response = repeatable_request(
                url=APPLE_URL, json=data, headers=APPLE_HEADERS
            ).json()

        if response["status"] == 21007:  # this is sandbox
            is_sandbox = True
            response = repeatable_request(
                url=APPLE_SANDBOX_URL, json=data, headers=APPLE_HEADERS
            ).json()

        if response["status"] == 0:
            products = response["receipt"]["in_app"]
            result = self.products_is_ok(products)

        return is_sandbox, result
