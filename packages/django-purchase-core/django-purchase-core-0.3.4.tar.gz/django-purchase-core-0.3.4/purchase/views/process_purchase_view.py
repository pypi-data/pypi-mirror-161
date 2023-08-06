import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from drf_yasg.utils import swagger_auto_schema

from rest_framework.parsers import JSONParser
from rest_framework.settings import api_settings

from purchase.views import ProcessTransactionBaseView
from purchase.models.choices import PurchaseResponseStatus
from purchase.serializers import PurchaseRequestSerialzier, PurchaseResponseSerializer
from purchase.controllers import PurchaseProcessController
from purchase.signals import purchase_completed

logger = logging.getLogger(__name__)


class ProcessPurchaseView(ProcessTransactionBaseView):
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
    def use_user(self):
        try:
            use_user = settings.PURCHASE_USER_ATTACHED
        except (ImproperlyConfigured, AttributeError):
            return False
        return use_user

    @property
    def permission_classes(self):
        if not self.use_user:
            return []
        return api_settings.DEFAULT_PERMISSION_CLASSES

    @property
    def authentication_classes(self):
        if not self.use_user:
            return []
        return api_settings.DEFAULT_AUTHENTICATION_CLASSES

    @property
    def status_choices(self):
        return PurchaseResponseStatus

    @property
    def controller_class(self):
        return PurchaseProcessController

    @property
    def signal(self):
        return purchase_completed
