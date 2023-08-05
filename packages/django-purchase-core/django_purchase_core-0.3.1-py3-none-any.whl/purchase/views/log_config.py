from rest_framework.parsers import JSONParser
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend

from purchase.models import Config
from purchase.serializers.config_response_serializer import ConfigResponseSerializer


class MonthlyPredictionFilter(filters.FilterSet):
    platform = filters.CharFilter(method="platform_filter", required=True)

    def platform_filter(self, _queryset, _name, value):
        self.queryset = self.queryset.filter(platform=value)
        return self.queryset

    class Meta:
        model = Config
        fields = ("platform", )


class LogConfig(RetrieveAPIView):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MonthlyPredictionFilter
    queryset = Config.objects.all()
    serializer_class = ConfigResponseSerializer
    parser_classes = [JSONParser]
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        config = get_object_or_404(queryset)
        return config
