import logging

from rest_framework import serializers

from purchase.models.choices import Platform


logger = logging.getLogger(__name__)


class FbSerializer(serializers.Serializer):
    """fb field of ChargeDataSerializer"""

    user_id = serializers.CharField(max_length=500, required=True, allow_null=True)
    advertiser_tracking_enabled = serializers.BooleanField(required=True)
    application_tracking_enabled = serializers.BooleanField(required=True)
    product_quantity = serializers.IntegerField(required=True)
    product_title = serializers.CharField(required=True)
    product_description = serializers.CharField(required=True)
    num_items = serializers.IntegerField(required=True)
    transaction_date = serializers.CharField(max_length=40, required=True)
    extinfo = serializers.ListField(
        child=serializers.CharField(allow_blank=True), required=True
    )


class ReceiptSerializer(serializers.Serializer):
    """receipt_data field of ChargeDataSerializer"""

    store = serializers.CharField(required=True)
    transaction_id = serializers.CharField(required=True)
    payload = serializers.CharField(required=True)


class PurchaseDataSerializer(serializers.Serializer):
    """data field of ChargeRequestSerializer"""

    receipt_data = ReceiptSerializer(required=True)
    appsflyer_id = serializers.CharField(max_length=100, required=False)
    adjust_device_id = serializers.CharField(max_length=255, required=False)
    product_id = serializers.CharField(required=True)
    advertiser_id = serializers.CharField(required=True, allow_null=True)
    value_to_sum = serializers.FloatField(required=True)
    currency = serializers.CharField(required=True, max_length=18)
    bundle_short_version = serializers.CharField(max_length=10, required=False)
    log_time = serializers.IntegerField(required=True)
    fb = FbSerializer(required=False)


class PurchaseRequestSerialzier(serializers.Serializer):
    platform = serializers.ChoiceField(
        choices=Platform.choices, required=True, write_only=True
    )
    is_sandbox = serializers.BooleanField(required=True, write_only=True)
    data = PurchaseDataSerializer(required=True, write_only=True)
