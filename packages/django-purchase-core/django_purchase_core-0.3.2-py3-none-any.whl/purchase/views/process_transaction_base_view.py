import logging

from django.contrib.auth.models import AnonymousUser
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.generics import CreateAPIView

from purchase.exceptions import CustomStatus

logger = logging.getLogger(__name__)


class ProcessTransactionBaseView(CreateAPIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        request_data = self.request_serializer(data=request.data)
        request_data.is_valid(raise_exception=True)
        request_data = request_data.validated_data
        self.update_data(request_data)
        try:
            response = self.process(data=request_data)
            return response
        except CustomStatus as cs:
            return Response(data=self.get_response_data(cs.message), status=200)
        except Exception as err:
            logger.log(logging.ERROR, err)
            return Response(data=self.get_response_data(self.status_choices.error), status=200)

    @property
    def status_choices(self):
        raise NotImplementedError

    @property
    def controller_class(self):
        raise NotImplementedError

    @property
    def signal(self):
        raise NotImplementedError

    @property
    def request_serializer(self):
        raise NotImplementedError

    @property
    def response_serializer(self):
        raise NotImplementedError

    @property
    def use_user(self):
        raise NotImplementedError

    def update_data(self, request_data: dict):
        if hasattr(self.request, "user") and not isinstance(self.request.user, AnonymousUser) and self.use_user:
            request_data.update({"user": self.request.user})
        else:
            request_data.update({"user": None})

    def process(self, data: dict):
        purchase = self.controller_class(serializer_data=data)

        if purchase.is_create:
            raise CustomStatus(self.status_choices.already_created)

        create_is_done, purchase_model = purchase.try_to_create()
        if not create_is_done:
            raise CustomStatus(self.status_choices.data_is_not_valid)

        is_sandbox, is_valid = purchase.verify()
        if is_sandbox:
            response_data = self.get_response_data(status=self.status_choices.ok)
            return Response(data=response_data, status=200)

        if is_valid:
            if hasattr(purchase, "lc"):
                purchase.lc.log(purchase_obj=purchase_model)
        else:
            purchase_model.set_transaction_id_to_fake()

        response_data = self.get_response_data(status=self.status_choices.ok)

        if self.use_user:
            self.signal.send(sender=self.__class__, instance=purchase)

        return Response(data=response_data, status=200)

    def get_response_data(self, status: str, error: str = None):
        serializable_data = {"status": status}
        if error:
            serializable_data.update({"error": error})
        response_data = self.response_serializer(data=serializable_data)
        response_data.is_valid(raise_exception=True)
        return response_data.validated_data
