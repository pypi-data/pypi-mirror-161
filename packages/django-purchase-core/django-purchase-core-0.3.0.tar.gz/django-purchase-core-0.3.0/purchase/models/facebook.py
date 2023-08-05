from django.db import models

from purchase.models.choices import Platform

GRAPH_API_VERSION = "v9.0"


class Facebook(models.Model):
    app_id = models.CharField(max_length=100)
    client_secret = models.CharField(max_length=100)
    platform = models.CharField(choices=Platform.choices, max_length=20, unique=True)

    @property
    def app_access_token(self) -> str:
        """Get app fb access token as access_token={app-id}|{client-token}"""
        return f"{self.app_id}|{self.client_secret}"

    class Meta:
        verbose_name_plural = "Facebook"
