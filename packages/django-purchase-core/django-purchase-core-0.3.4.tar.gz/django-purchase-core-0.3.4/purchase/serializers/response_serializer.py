from rest_framework import serializers

from purchase.models.choices import PurchaseResponseStatus


class PurchaseResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=PurchaseResponseStatus.choices,
        required=True,
    )
    error = serializers.CharField(required=False)
