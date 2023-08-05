import json
import logging

from django.db import transaction

from purchase.models.choices import Platform
from purchase.verifiers import AppleVerifier, GoogleVerifier
from purchase.models import Purchase
from purchase.strings.log_levels import (
    PURCHASE_CREATE,
    GOOGLE_ERROR_LEVEL,
    APPLE_ERROR_LEVEL,
)
from purchase.controllers import LogController

logger = logging.getLogger(__name__)


class PurchaseProcessController:
    def __init__(self, serializer_data: dict):
        self.serializer_data = serializer_data
        self.platform = serializer_data["platform"]
        self.fb = serializer_data["data"]["fb"]
        self.version = self.fb["bundle_short_version"]
        self.is_sandbox = serializer_data["is_sandbox"]
        self.receipt_data = serializer_data["data"]["receipt_data"]
        self.lc = LogController(
            self.platform, self.version, self.fb, self.transaction_id, self.serializer_data
        )

    @property
    def transaction_id(self):
        if self.platform == Platform.android:
            return self.get_transaction_id_from_json()
        else:
            return self.serializer_data["data"]["receipt_data"]["transaction_id"]

    def get_transaction_id_from_json(self):
        try:
            payload = json.loads(self.receipt_data["payload"])
            payload_json = json.loads(payload["json"])
            return payload_json["orderId"]
        except Exception as err:
            logger.error(
                f"JSON parsing of transaction_id from payload on Android: {err}"
            )

    @property
    def is_create(self):
        return Purchase.objects.filter(
            transaction_id=self.transaction_id, platform=self.platform
        ).exists()

    @transaction.atomic
    def create(self):
        return Purchase.objects.create(
            transaction_id=self.transaction_id,
            advertiser_id=self.fb["advertiser_id"],
            platform=self.platform,
            fb_user_id=self.fb["user_id"],
            bundle_short_version=self.fb["bundle_short_version"],
            ext_info=self.fb["extinfo"],
            product_id=self.fb["product_id"],
            value_to_sum=self.fb["value_to_sum"],
            log_time=self.fb["log_time"],
            currency=self.fb["currency"],
            is_sandbox=self.is_sandbox,
            body=self.serializer_data
        )

    def try_to_create(self) -> (bool, Purchase or bool):
        try:
            purchase_obj = self.create()
            return True, purchase_obj
        except Exception as err:
            self.lc.save_error_log(
                error_message=str(err),
                log_level=PURCHASE_CREATE,
                details=self.serializer_data,
            )
            return False, False

    def verify(self) -> (bool, bool):
        if self.platform == Platform.android:
            return self.google_verify()
        return self.apple_verify()

    def apple_verify(self) -> (bool, bool):
        is_sandbox = self.is_sandbox
        result = False
        try:
            apple_verifier = AppleVerifier(
                receipt=self.receipt_data,
                is_sandbox=self.is_sandbox,
                product_id=self.serializer_data["data"]["fb"]["product_id"],
                platform=self.platform,
                version=self.version,
                transaction_id=self.transaction_id,
            )
            is_sandbox, result = apple_verifier.verify()
        except Exception as err:
            details = {
                "transaction_id": self.transaction_id,
                "receipt": self.receipt_data,
            }
            self.lc.save_error_log(
                error_message=str(err), log_level=APPLE_ERROR_LEVEL, details=details
            )
        return is_sandbox, result

    def google_verify(self) -> (bool, bool):
        result = False
        try:
            google_verifier = GoogleVerifier(
                receipt=self.receipt_data,
                platform=self.platform,
                version=self.version,
            )
            result = google_verifier.verify()
        except Exception as err:
            details = {
                "transaction_id": self.transaction_id,
                "receipt": self.receipt_data,
            }
            self.lc.save_error_log(
                error_message=str(err), log_level=GOOGLE_ERROR_LEVEL, details=details
            )
        return self.is_sandbox, result
