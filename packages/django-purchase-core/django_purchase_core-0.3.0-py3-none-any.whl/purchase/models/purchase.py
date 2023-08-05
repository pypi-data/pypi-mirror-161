from django.db import models

from purchase.models.choices import Platform


class Purchase(models.Model):
    """Model of Purchases from games"""

    currency = models.CharField(max_length=25)
    log_time = models.CharField(max_length=11)
    ext_info = models.CharField(max_length=255)
    product_id = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=255)
    bundle_short_version = models.CharField(max_length=255)
    fb_user_id = models.CharField(max_length=255, null=True)
    advertiser_id = models.CharField(max_length=255, null=True)
    platform = models.CharField(max_length=8, choices=Platform.choices)

    value_to_sum = models.FloatField()

    body = models.JSONField()

    is_valid = models.BooleanField(default=False)
    is_sandbox = models.BooleanField(default=False)
    fb_is_logged = models.BooleanField(default=False)
    af_is_logged = models.BooleanField(default=False)
    adjust_is_logged = models.BooleanField(default=False)

    def set_transaction_id_to_fake(self):
        self.transaction_id = f"fake_{self.transaction_id}"
        self.save()
