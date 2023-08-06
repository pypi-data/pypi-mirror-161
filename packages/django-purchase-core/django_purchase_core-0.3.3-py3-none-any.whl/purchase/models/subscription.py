import logging

from django.db import models
from django.utils import timezone
from django.conf import settings

from purchase.models.choices import Platform
from purchase.verifiers import AppleVerifier, GoogleVerifier

logger = logging.getLogger(__name__)


class Subscription(models.Model):
    user = models.ForeignKey(to=settings.USER_MODEL, on_delete=models.SET_NULL, null=True)

    currency = models.CharField(max_length=25)
    log_time = models.CharField(max_length=11)
    ext_info = models.CharField(max_length=255, null=True)
    product_id = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=255)
    bundle_short_version = models.CharField(max_length=255)
    fb_user_id = models.CharField(max_length=255, null=True)
    advertiser_id = models.CharField(max_length=255, null=True)
    platform = models.CharField(max_length=8, choices=Platform.choices)

    value_to_sum = models.FloatField()

    body = models.JSONField()

    is_sandbox = models.BooleanField(default=False)

    active_till = models.DateTimeField(null=True)
    google_token = models.CharField(null=True, max_length=8192, help_text="Only for android platform")
    _is_active = models.DateField(null=True)
    _expired = models.BooleanField(default=False)

    def __verify(self):
        try:
            if self.platform == Platform.ios:
                return AppleVerifier(
                    receipt=self.body["data"]["receipt_data"],
                    is_sandbox=self.is_sandbox,
                    product_id=self.product_id,
                    platform=self.platform,
                    version=self.body["data"]["fb"]["bundle_short_version"],
                    transaction_id=self.transaction_id,
                    is_sub=True,
                )
            return self.is_sandbox, GoogleVerifier(
                receipt=self.body["data"]["receipt_data"],
                platform=self.platform,
                version=self.body["data"]["fb"]["bundle_short_version"],
                is_sub=True,
            )
        except Exception as err:
            logger.error(str(err))
            return False, False

    @property
    def is_active(self):
        if self._expired:
            return False
        today = timezone.now().today()
        if today == self._is_active:
            return True
        _, active = self.__verify()
        if not active:
            self._expired = True
        self._is_active = today
        self.save()
        return not self._expired

    def set_transaction_id_to_fake(self):
        self.transaction_id = f"fake_{self.transaction_id}"
        self.save()
