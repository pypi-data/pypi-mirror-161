from django.db import models


class Platform(models.TextChoices):
    ios = "ios", "Ios"
    android = "android", "Android"


class PurchaseResponseStatus(models.TextChoices):
    ok = "ok"
    already_created = "purchase already created"
    data_is_not_valid = "data is not valid"
    error = "error"


class SubscriptionResponseStatus(models.TextChoices):
    ok = "ok"
    already_created = "subscription already created"
    data_is_not_valid = "data is not valid"
    error = "error"
