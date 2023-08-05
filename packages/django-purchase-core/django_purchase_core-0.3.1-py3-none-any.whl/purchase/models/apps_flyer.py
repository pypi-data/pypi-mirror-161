from django.db import models

from purchase.models.choices import Platform


class AppsFlyer(models.Model):
    app_id = models.CharField(max_length=100)
    dev_key = models.CharField(max_length=300)
    platform = models.CharField(choices=Platform.choices, max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "AppsFlyer"
