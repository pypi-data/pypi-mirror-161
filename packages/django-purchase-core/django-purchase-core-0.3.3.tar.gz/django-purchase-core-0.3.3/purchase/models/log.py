from django.db import models

from purchase.models.choices import Platform


class Log(models.Model):
    """Error logs when making purchases"""

    version = models.CharField(max_length=10, null=True)
    log_level = models.CharField(max_length=15, null=True, blank=True)
    platform = models.CharField(choices=Platform.choices, max_length=20)

    message = models.TextField()

    details = models.JSONField(null=True, blank=True)

    time = models.DateTimeField(auto_now_add=True)
