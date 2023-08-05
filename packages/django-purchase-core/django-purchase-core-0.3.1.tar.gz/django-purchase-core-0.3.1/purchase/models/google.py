from django.db import models
from django.forms.models import model_to_dict


class Google(models.Model):
    client_id = models.CharField(max_length=50)
    project_id = models.CharField(max_length=50)
    private_key_id = models.CharField(max_length=60)
    type = models.CharField(max_length=20, default="service_account")

    private_key = models.TextField()

    client_email = models.EmailField()

    auth_uri = models.URLField()
    token_uri = models.URLField()
    client_x509_cert_url = models.URLField()
    auth_provider_x509_cert_url = models.URLField()

    class Meta:
        verbose_name_plural = "Google"

    @property
    def as_dict(self):  # pragma: no cover
        return model_to_dict(
            self,
            exclude=["id", "game"],
        )
