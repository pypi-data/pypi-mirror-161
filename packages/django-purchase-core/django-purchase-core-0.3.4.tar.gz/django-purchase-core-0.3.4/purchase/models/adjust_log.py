from django.db import models


class AdjustLog(models.Model):
    """Adjust logs"""

    purchase = models.OneToOneField(
        to="purchase.Purchase", on_delete=models.CASCADE, related_name="adjust_log"
    )

    request_url = models.URLField()

    response = models.JSONField()
    request_data = models.JSONField()
    request_headers = models.JSONField()

    created_at = models.DateTimeField(auto_now=True)
