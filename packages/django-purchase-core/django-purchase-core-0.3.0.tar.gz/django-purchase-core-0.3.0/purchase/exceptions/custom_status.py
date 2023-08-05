from typing import Union
from rest_framework import status


class CustomStatus(Exception):
    status_code = status.HTTP_200_OK
    message = "Status"
    details = ""

    def __init__(
        self,
        message: Union[str, int] = None,
        details: str = None,
    ):
        self.message = message or self.message
        self.details = details or self.details

    def __str__(self):
        details = f": {self.details}" if self.details else ""
        return f"{self.message}{details}"
