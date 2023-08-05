import logging

from drf_yasg.utils import swagger_auto_schema

from rest_framework.parsers import JSONParser

from purchase.views import ProcessTransactionBaseView
from purchase.models.choices import SubscriptionResponseStatus
from purchase.serializers import PurchaseRequestSerialzier, SubscriptionResponseSerializer
from purchase.controllers import SubscriptionController
from purchase.signals import subscription_completed

logger = logging.getLogger(__name__)


class ProcessSubscriptionView(ProcessTransactionBaseView):
    parser_classes = [JSONParser]
    request_serializer = PurchaseRequestSerialzier
    response_serializer = SubscriptionResponseSerializer

    @swagger_auto_schema(
        responses={200: response_serializer()},
        request_body=request_serializer(),
        operation_id="Process Subscription",
        tags=["Subscription"],
        operation_description=(
            "API to provide validating subscriptions from AppStore or GooglePlay.<br>"
            "Statuses:<br>"
            "1. ok - ok :)<br>"
            "2. subscription already created - subscription with given payload was already processed<br>"
            "3. data is not valid - provided data is not valid to create purchase<br>"
            "4. error - some error occurred, check logs"
        ),
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @property
    def status_choices(self):
        return SubscriptionResponseStatus

    @property
    def controller_class(self):
        return SubscriptionController

    @property
    def signal(self):
        return subscription_completed

    @property
    def use_user(self):
        return True
