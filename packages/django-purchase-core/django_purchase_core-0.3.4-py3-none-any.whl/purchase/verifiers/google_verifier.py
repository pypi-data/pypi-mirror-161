import json
import logging

from dataclasses import dataclass

from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

from purchase.models import Google as GoogleModel
from purchase.strings.verifiers import GOOGLE_AUTH_URL

logger = logging.getLogger(__name__)


@dataclass
class GoogleVerifier:
    receipt: dict
    platform: str
    version: str
    is_sub: bool = False

    @property
    def payload(self) -> dict:
        payload = self.receipt["payload"]
        if isinstance(payload, str):
            payload = json.loads(payload)
        return json.loads(payload["json"])

    @property
    def url(self) -> str:
        package_name = self.payload["packageName"]
        product_id = self.payload["productId"]
        token = self.payload["purchaseToken"]
        base_url = "https://www.googleapis.com/androidpublisher/v3/applications/"
        url_type = "products" if not self.is_sub else "subscriptions"
        data_url = f"{package_name}/purchases/{url_type}/{product_id}/tokens/{token}"
        return base_url + data_url

    def verify(self) -> bool:
        associated_google_model = GoogleModel.objects.first()
        if not associated_google_model.exists():
            return False
        instance = associated_google_model.first()
        kwargs = instance.as_dict
        kwargs["private_key"] = kwargs["private_key"].replace("\\n", "\n")
        credentials = service_account.Credentials.from_service_account_info(kwargs)
        credentials = credentials.with_scopes([GOOGLE_AUTH_URL])
        session = AuthorizedSession(credentials)
        response = session.get(self.url)
        return response.status_code == 200
