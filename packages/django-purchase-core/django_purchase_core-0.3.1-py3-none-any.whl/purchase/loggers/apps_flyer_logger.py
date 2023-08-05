import json
import logging
import requests

from datetime import datetime
from dataclasses import dataclass
from django.shortcuts import get_object_or_404

from purchase.models import AppsFlyer
from purchase.utils import repeatable_request

logger = logging.getLogger(__name__)


@dataclass
class AppsFlyerLogger:
    platform: str
    appsflyer_id: str
    fb: dict

    def log_purchase(self) -> requests.Response:
        response = repeatable_request(
            url=self._get_url(), json=self._get_data(), headers=self._get_headers()
        )
        return response

    @property
    def _credentials(self):
        credentials = get_object_or_404(
            AppsFlyer, platform=self.platform
        )
        return credentials

    @property
    def _time_format(self):
        return "%Y-%m-%d %H-%M-%S.000"

    def _get_data(self):
        data = {
            "appsflyer_id": self.appsflyer_id,
            "advertising_id": self.fb["advertiser_id"],
            "app_version_name": self.fb["bundle_short_version"],
            "eventTime": datetime.fromtimestamp(self.fb["log_time"]).strftime(
                self._time_format
            ),
            "eventName": "af_purchase",
            "eventCurrency": self.fb["currency"],
            "eventValue": json.dumps(
                {
                    "af_revenue": self.fb["value_to_sum"],
                    "af_content_type": "In-App Purchase",
                    "af_content_id": self.fb["product_id"],
                    "af_quantity": 1,
                }
            ),
        }

        if len(self.fb["extinfo"]) >= 2:
            data["bundleIdentifier"] = self.fb["extinfo"][1]

        return data

    def _get_headers(self):
        return {"authentication": self._credentials.dev_key}

    def _get_url(self):
        return f"https://api2.appsflyer.com/inappevent/{self._credentials.app_id}"
