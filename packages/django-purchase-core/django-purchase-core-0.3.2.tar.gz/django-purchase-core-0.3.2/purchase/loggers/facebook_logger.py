import logging
import requests

from datetime import datetime
from dataclasses import dataclass
from django.shortcuts import get_object_or_404

from purchase.models import Facebook
from purchase.utils import repeatable_request
from purchase.models.facebook import GRAPH_API_VERSION

logger = logging.getLogger(__name__)


@dataclass
class FacebookLogger:
    platform: str
    transaction_id: str
    fb_data: dict

    @property
    def _credentials(self):
        credentials = get_object_or_404(
            Facebook, platform=self.platform
        )
        return credentials

    def log_purchase(self) -> requests.Response:
        response = repeatable_request(
            url=self._get_url(), json=self._get_data(), headers=self._get_headers()
        )
        return response

    def _get_data(self) -> dict:
        return {
            "event": "CUSTOM_APP_EVENTS",
            "advertiser_id": self.fb_data["advertiser_id"],
            "bundle_version": self.fb_data["bundle_short_version"],
            "bundle_short_version": self.fb_data["bundle_short_version"],
            "app_user_id": self.fb_data["user_id"],
            "advertiser_tracking_enabled": str(
                int(self.fb_data["advertiser_tracking_enabled"])
            ),
            "application_tracking_enabled": "1",
            "extinfo": self.fb_data["extinfo"],
            "custom_events": [
                {
                    "_logTime": int(datetime.now().timestamp()),
                    "fb_transaction_date": self.fb_data["transaction_date"],
                    "Transaction Identifier": self.transaction_id,
                    "fb_content": [{"id": self.fb_data["product_id"], "quantity": 1}],
                    "_valueToSum": self.fb_data["value_to_sum"],
                    "fb_currency": self.fb_data["currency"],
                    "Product Title": self.fb_data["product_title"],
                    "fb_num_items": 1,
                    "fb_content_type": "product",
                    "fb_iap_product_type": "inapp",
                    "_eventName": "fb_mobile_purchase",
                }
            ],
        }

    def _get_headers(self) -> dict:
        return {"Authorization": f"Bearer {self._credentials.app_access_token}"}

    def _get_url(self) -> str:
        return f"https://graph.facebook.com/{GRAPH_API_VERSION}/{self._credentials.app_id}/activities"
