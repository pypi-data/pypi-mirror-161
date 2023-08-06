import logging

from purchase.models import Subscription
from purchase.verifiers import AppleVerifier, GoogleVerifier
from purchase.controllers import ProcessControllerABC


logger = logging.getLogger(__name__)


class SubscriptionController(ProcessControllerABC):
    model = Subscription
    logging_enabled = False

    def apple_verify(self) -> (bool, bool):
        is_sandbox = self.is_sandbox
        result = False
        try:
            apple_verifier = AppleVerifier(
                receipt=self.receipt_data,
                is_sandbox=self.is_sandbox,
                product_id=self.serializer_data["data"]["product_id"],
                platform=self.platform,
                version=self.version,
                transaction_id=self.transaction_id,
                is_sub=True,
            )
            is_sandbox, result = apple_verifier.verify()
        except Exception as err:
            logger.error(str(err))
        return is_sandbox, result

    def google_verify(self) -> (bool, bool):
        result = False
        try:
            google_verifier = GoogleVerifier(
                receipt=self.receipt_data,
                platform=self.platform,
                version=self.version,
                is_sub=True,
            )
            result = google_verifier.verify()
        except Exception as err:
            logger.error(str(err))
        return self.is_sandbox, result
