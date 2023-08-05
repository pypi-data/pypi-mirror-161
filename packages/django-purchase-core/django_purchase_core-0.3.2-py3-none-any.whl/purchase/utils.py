import time
import logging
import requests

from typing import Union


logger = logging.getLogger(__name__)


def repeatable_request(
    url: str,
    params: dict = None,
    data: Union[str, dict] = None,
    json: dict = None,
    headers: dict = None,
    trying: int = 3,
) -> requests.Response:
    response = request(url, params, data, json, headers)
    while trying and response.status_code != 200:
        trying -= 1
        time.sleep(0.1)

    if response.status_code != 200:
        error_text = f"api error: request error [{url}] {response.status_code = }, {response.text = }"
        logger.exception(error_text)
    return response


def request(url, params, data, json, headers):
    response = requests.post(
        url=url, params=params, data=data, json=json, headers=headers
    )
    response_text = response.text  # for debugging in sentry  # noqa: F841
    return response
