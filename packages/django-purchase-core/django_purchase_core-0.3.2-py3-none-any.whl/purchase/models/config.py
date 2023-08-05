from django.db import models

from purchase.models.choices import Platform


class Config(models.Model):
    """Model for setting purchase logging settings"""

    platform = models.CharField(choices=Platform.choices, max_length=20, unique=True)

    is_fb_log_enabled = models.BooleanField(default=True)
    is_af_log_enabled = models.BooleanField(default=True)
    is_adjust_log_enabled = models.BooleanField(default=True)
