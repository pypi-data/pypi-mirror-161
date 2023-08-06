import time
import logging
import requests

from dataclasses import dataclass
from django.shortcuts import get_object_or_404

from purchase.models import Adjust
from purchase.strings.loggers import ADJUST_URL
from purchase.utils import repeatable_request

logger = logging.getLogger(__name__)


@dataclass
class AdjustLogger:
    fb: dict
    platform: str
    advertiser_id: str
    advertiser_key: str
    value_to_sum: float
    currency: str

    @property
    def credentials(self) -> Adjust:
        credentials = get_object_or_404(Adjust, platform=self.platform)
        return credentials

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.credentials.authorization_token}"}

    def log_purchase(self) -> requests.Response:
        response = repeatable_request(
            url=ADJUST_URL, data=self.get_data(), headers=self.headers
        )
        return response

    def get_data(self) -> dict:
        return {
            "revenue": self.value_to_sum,
            "currency": self.currency,
            "event_token": self.credentials.purchase_event_token,
            "app_token": self.credentials.app_token,
            "s2s": 1,
            self.advertiser_key: self.advertiser_id,
            "created_at_unix": int(time.time()),
        }
