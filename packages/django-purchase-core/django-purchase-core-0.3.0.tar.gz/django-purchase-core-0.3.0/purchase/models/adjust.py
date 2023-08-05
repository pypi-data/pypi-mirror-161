from django.db import models

from purchase.models.choices import Platform


class Adjust(models.Model):
    app_token = models.CharField(max_length=50)
    authorization_token = models.CharField(max_length=50)
    purchase_event_token = models.CharField(max_length=50)
    platform = models.CharField(choices=Platform.choices, max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "Adjust"
