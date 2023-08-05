from rest_framework import serializers

from purchase.models.choices import SubscriptionResponseStatus


class SubscriptionResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=SubscriptionResponseStatus.choices,
        required=True,
    )
    error = serializers.CharField(required=False)
