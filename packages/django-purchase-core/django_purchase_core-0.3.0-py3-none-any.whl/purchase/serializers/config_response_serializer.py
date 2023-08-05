from purchase.models import Config
from rest_framework import serializers


class ConfigResponseSerializer(serializers.ModelSerializer):
    fb = serializers.BooleanField(required=True, source="is_fb_log_enabled")
    apps_flyer = serializers.BooleanField(required=True, source="is_af_log_enabled")
    adjust = serializers.BooleanField(required=True, source="is_adjust_log_enabled")

    class Meta:
        model = Config
        fields = ("fb", "apps_flyer", "adjust")
