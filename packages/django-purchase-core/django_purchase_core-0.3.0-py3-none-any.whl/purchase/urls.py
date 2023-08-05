from django.urls import path

from .views import ProcessPurchaseView, LogConfig, ProcessSubscriptionView

urlpatterns = [
    path("chargeverify/", ProcessPurchaseView.as_view(), name="ChargeVerify"),
    path("subverify/", ProcessSubscriptionView.as_view(), name="SubscriptionVerify"),
    path("logconfig/", LogConfig.as_view(), name="LogConfig"),
]
