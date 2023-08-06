import logging

from purchase.models import Log, Purchase, AdjustLog, Config
from purchase.models.choices import Platform
from purchase.strings.loggers import ADJUST_URL
from purchase.loggers import AdjustLogger, FacebookLogger, AppsFlyerLogger
from purchase.strings.errors import APPSFLYER_ID_NOT_FOUND, ALL_ZEROS, ADJUST_ADVERTISER_NOT_FOUND
from purchase.strings.log_levels import (
    FACEBOOK_LOGGING_ERROR_LEVEL,
    ADJUST_ERROR_LEVEL,
    APPS_FLYER_ERROR_LEVEL,
)

logger = logging.getLogger(__name__)


class LogController:
    def __init__(self, platform, version, fb, transaction_id, serializer_data):
        self.platform = platform
        self.version = version
        self.fb = fb
        self.transaction_id = transaction_id
        self.serializer_data = serializer_data

    @property
    def appsflyer_id(self):
        if (
            "appsflyer_id" not in self.serializer_data["data"]
            or self.serializer_data["data"]["appsflyer_id"] is None
        ):  # pragma: no cover
            raise ValueError(APPSFLYER_ID_NOT_FOUND)
        return self.serializer_data["data"]["appsflyer_id"]

    def get_advertiser_id(self):
        advertiser_id = self.serializer_data["data"]["advertiser_id"]
        if advertiser_id is None or advertiser_id == ALL_ZEROS or advertiser_id == "":
            if "adjust_device_id" not in self.serializer_data["data"]:
                raise ValueError(ADJUST_ADVERTISER_NOT_FOUND)
            return "adid", self.serializer_data["data"]["adjust_device_id"]
        if self.platform == Platform.android:
            return "gps_adid", advertiser_id
        return "idfa", advertiser_id

    def get_details_for_log(self):
        return {"transaction_id": self.transaction_id, "data": self.serializer_data}

    def save_error_log(self, error_message: str, log_level: str, details: dict):
        Log.objects.create(
            platform=self.platform,
            version=self.version,
            log_level=log_level,
            message=error_message,
            details=details,
        )

    def handle_logger(self,
                      purchase_obj: Purchase,
                      out_logger: FacebookLogger or AppsFlyerLogger or AdjustLogger,
                      error_level,
                      log_field: str) -> str:
        response = out_logger.log_purchase()
        if response.status_code != 200:
            err = f"api error: request error [{response.url}] {response.status_code = }, {response.text = }"
            self.save_error_log(
                error_message=err,
                log_level=error_level,
                details=self.get_details_for_log(),
            )
        else:
            setattr(purchase_obj, log_field, True)
            purchase_obj.save()
        return response.text

    def log_in_facebook(self, purchase_obj: Purchase):
        fb_logger = FacebookLogger(
            platform=self.platform,
            transaction_id=self.transaction_id,
            fb_data=self.fb,
            advertiser_id=self.serializer_data["data"]["advertiser_id"],
            bundle_short_version=self.version,
            product_id=self.serializer_data["data"]["product_id"],
            value_to_sum=self.serializer_data["data"]["value_to_sum"],
            currency=self.serializer_data["data"]["currency"],
        )
        self.handle_logger(purchase_obj, fb_logger, FACEBOOK_LOGGING_ERROR_LEVEL, "fb_is_logged")

    def log_in_appsflyer(self, purchase_obj: Purchase):
        appsflyer_logger = AppsFlyerLogger(
            platform=self.platform,
            appsflyer_id=self.appsflyer_id,
            fb=self.fb,
            bundle_short_version=self.version,
            currency=self.serializer_data["data"]["currency"],
            value_to_sum=self.serializer_data["data"]["value_to_sum"],
            product_id=self.serializer_data["data"]["product_id"],
            advertiser_id=self.serializer_data["data"]["advertiser_id"],
            log_time=self.serializer_data["data"]["log_time"]
        )
        self.handle_logger(purchase_obj, appsflyer_logger, APPS_FLYER_ERROR_LEVEL, "af_is_logged")

    def log_in_adjust(self, purchase_obj: Purchase):
        advertiser_key, advertiser_id = self.get_advertiser_id()
        adjust_logger = AdjustLogger(
            fb=self.fb,
            platform=self.platform,
            advertiser_id=advertiser_id,
            advertiser_key=advertiser_key,
            value_to_sum=self.serializer_data["data"]["value_to_sum"],
            currency=self.serializer_data["data"]["currency"],
        )
        text = self.handle_logger(purchase_obj, adjust_logger, ADJUST_ERROR_LEVEL, "adjust_is_logged")
        AdjustLog.objects.get_or_create(
            purchase=purchase_obj,
            request_url=ADJUST_URL,
            response=text,
            request_data=adjust_logger.get_data(),
            request_headers=adjust_logger.headers,
        )

    def get_enable_loggers(self):
        config = Config.objects.filter(platform=self.platform)
        loggers = [
            self.log_in_adjust if not config.exists() or config.first().is_adjust_log_enabled else None,
            self.log_in_appsflyer if not config.exists() or config.first().is_af_log_enabled else None,
            self.log_in_facebook if not config.exists() or config.first().is_fb_log_enabled else None,
        ]
        return loggers

    def log(self, purchase_obj: Purchase):
        enabled_loggers = self.get_enable_loggers()
        for out_logger in enabled_loggers:
            if out_logger is None:
                continue
            out_logger(purchase_obj=purchase_obj)
