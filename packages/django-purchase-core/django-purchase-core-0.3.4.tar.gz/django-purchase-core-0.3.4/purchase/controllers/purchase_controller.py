import logging

from purchase.verifiers import AppleVerifier, GoogleVerifier
from purchase.models import Purchase
from purchase.strings.log_levels import (
    GOOGLE_ERROR_LEVEL,
    APPLE_ERROR_LEVEL,
)
from purchase.controllers import ProcessControllerABC

logger = logging.getLogger(__name__)


class PurchaseProcessController(ProcessControllerABC):
    model = Purchase
    logging_enabled = True

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
            )
            is_sandbox, result = apple_verifier.verify()
        except Exception as err:
            details = {
                "transaction_id": self.transaction_id,
                "receipt": self.receipt_data,
            }
            self.lc.save_error_log(
                error_message=str(err), log_level=APPLE_ERROR_LEVEL, details=details
            )
        return is_sandbox, result

    def google_verify(self) -> (bool, bool):
        result = False
        try:
            google_verifier = GoogleVerifier(
                receipt=self.receipt_data,
                platform=self.platform,
                version=self.version,
            )
            result = google_verifier.verify()
        except Exception as err:
            details = {
                "transaction_id": self.transaction_id,
                "receipt": self.receipt_data,
            }
            self.lc.save_error_log(
                error_message=str(err), log_level=GOOGLE_ERROR_LEVEL, details=details
            )
        return self.is_sandbox, result
