import json
import logging
from abc import ABC, abstractmethod

from django.db import transaction

from purchase.controllers import LogController
from purchase.models.choices import Platform
from purchase.strings.log_levels import PURCHASE_CREATE

logger = logging.getLogger(__name__)


class ProcessControllerABC(ABC):
    def __init__(self, serializer_data: dict):
        self.serializer_data = serializer_data
        self.platform = serializer_data["platform"]
        self.fb = serializer_data["data"]["fb"] if "fb" in serializer_data["data"] else None
        self.version = serializer_data["data"]["bundle_short_version"]
        self.is_sandbox = serializer_data["is_sandbox"]
        self.receipt_data = serializer_data["data"]["receipt_data"]
        self.user = serializer_data.pop("user")
        if self.logging_enabled:
            self.lc = LogController(self.platform, self.version, self.fb, self.transaction_id, self.serializer_data)

    @property
    @abstractmethod
    def model(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def logging_enabled(self):
        raise NotImplementedError

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

    @transaction.atomic
    def create(self):
        return self.model.objects.create(
            user=self.user,
            transaction_id=self.transaction_id,
            advertiser_id=self.serializer_data["data"]["advertiser_id"],
            platform=self.platform,
            fb_user_id=self.fb["user_id"] if self.fb else None,
            bundle_short_version=self.version,
            ext_info=self.fb["extinfo"] if self.fb else None,
            product_id=self.serializer_data["data"]["product_id"],
            value_to_sum=self.serializer_data["data"]["value_to_sum"],
            log_time=self.serializer_data["data"]["log_time"],
            currency=self.serializer_data["data"]["currency"],
            is_sandbox=self.is_sandbox,
            body=self.serializer_data
        )

    @property
    def is_create(self):
        return self.model.objects.filter(
            transaction_id=self.transaction_id, platform=self.platform
        ).exists()

    def try_to_create(self) -> (bool, model or bool):
        try:
            purchase_obj = self.create()
            return True, purchase_obj
        except Exception as err:
            if self.logging_enabled:
                self.lc.save_error_log(
                    error_message=str(err),
                    log_level=PURCHASE_CREATE,
                    details=self.serializer_data,
                )
            logger.error(str(err))
            return False, False

    def verify(self) -> (bool, bool):
        if self.platform == Platform.android:
            return self.google_verify()
        return self.apple_verify()

    @abstractmethod
    def google_verify(self):
        raise NotImplementedError

    @abstractmethod
    def apple_verify(self):
        raise NotImplementedError
