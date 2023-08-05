import logging

from drf_yasg.utils import swagger_auto_schema

from rest_framework.parsers import JSONParser

from purchase.views import ProcessTransactionBaseView
from purchase.models.choices import PurchaseResponseStatus
from purchase.serializers import PurchaseRequestSerialzier, PurchaseResponseSerializer
from purchase.controllers import PurchaseProcessController
from purchase.signals import purchase_completed

logger = logging.getLogger(__name__)


class ProcessPurchaseView(ProcessTransactionBaseView):
    permission_classes = []
    authentication_classes = []
    parser_classes = [JSONParser]
    request_serializer = PurchaseRequestSerialzier
    response_serializer = PurchaseResponseSerializer

    @swagger_auto_schema(
        responses={200: response_serializer()},
        request_body=request_serializer(),
        operation_id="Process Purchase",
        tags=["Purchase"],
        operation_description=(
            "API to provide validating purchases from AppStore or GooglePlay.<br>"
            "Statuses:<br>"
            "1. ok - ok :)<br>"
            "2. purchase already created - purchase with given payload was already processed<br>"
            "3. data is not valid - provided data is not valid to create purchase<br>"
            "4. error - some error occurred, check logs"
        ),
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @property
    def status_choices(self):
        return PurchaseResponseStatus

    @property
    def controller_class(self):
        return PurchaseProcessController

    @property
    def signal(self):
        return purchase_completed
