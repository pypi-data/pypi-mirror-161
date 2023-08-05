import json
from datetime import datetime
from functools import lru_cache

from django import forms
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import re_path, reverse
from django.utils.html import format_html
from django.contrib import admin, messages
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer
from rangefilter.filters import DateTimeRangeFilter
from django.core.exceptions import ValidationError

from purchase.models import (
    Config,
    Log,
    Purchase,
    AdjustLog,
    Facebook,
    Adjust,
    AppsFlyer,
    Google,
)


class FileUploadForm(forms.Form):
    file = forms.FileField()

    def replace_model(self, data):
        if isinstance(data, dict):
            if data["model"] == Google._meta.label_lower:
                self.data = data["fields"]
            else:
                self.add_error(
                    None,
                    f'JSON parse error: field model must be {Google._meta.label_lower}, found {data["model"]}',
                )
        else:
            self.add_error(None, "JSON parse error: root object must be <dict>")

    def clean_file(self):
        raw_data = self.cleaned_data["file"]
        for chunk in raw_data.chunks():
            data = json.loads(chunk)
            self.replace_model(data)
        return raw_data

    def save(self, instance):
        if self.data:
            instance.update(**self.data)
            return instance


class CustomDateTimeRangeFilter(DateTimeRangeFilter):
    def queryset(self, request: WSGIRequest, queryset):
        if self.form.is_valid():
            log_time_gte = str(
                int(self.form.cleaned_data["log_time__range__gte"].timestamp())
            )
            log_time_lte = str(
                int(self.form.cleaned_data["log_time__range__lte"].timestamp())
            )
            if log_time_gte and log_time_lte:
                return queryset.filter(log_time__range=(log_time_gte, log_time_lte))
        return queryset


@lru_cache()
def get_fb_credentials(platform):
    return Facebook.objects.filter(platform=platform).first()


def pretty_printed(obj, attr_name):
    """Function to display pretty version of our data"""
    # Convert the data to sorted, indented JSON
    response = json.dumps(getattr(obj, attr_name), sort_keys=True, indent=4)
    # Truncate the data. Alter as needed
    # response = response[:5000]  # noqa: E800
    # Get the Pygments formatter
    formatter = HtmlFormatter(style="colorful")
    # Highlight the data
    response = highlight(response, JsonLexer(), formatter)
    # Get the stylesheet
    style = "<style>" + formatter.get_style_defs() + "</style><br>"
    # Safe the output
    return mark_safe(style + response)  # noqa: S308, S703


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    readonly_fields = ("pretty_printed",)
    list_display = (
        "transaction_id",
        "version",
        "platform",
        "product_id",
        "value_to_sum",
        "currency",
        "time",
        "is_valid",
        "fb_is_logged",
        "af_is_logged",
        "adjust_is_logged",
        "is_sandbox",
    )
    list_display_links = ("transaction_id",)
    list_filter = (
        "platform",
        "is_valid",
        "fb_is_logged",
        "af_is_logged",
        "adjust_is_logged",
        "bundle_short_version",
        ("log_time", CustomDateTimeRangeFilter),
    )

    def get_rangefilter_logTime_default(self, _request):  # noqa: N802
        return timezone.datetime.today, timezone.datetime.today

    def get_rangefilter_logTime_title(self, _request, _field_path):  # noqa: N802
        return "Date Filter"

    def time(self, obj):
        return datetime.fromtimestamp(int(obj.log_time)).strftime("%Y-%m-%d %H:%M:%S")

    time.short_description = "Time"

    def version(self, obj):
        return obj.bundle_short_version

    version.short_description = "Version"

    def pretty_printed(self, obj):
        return pretty_printed(obj, "body")

    pretty_printed.short_description = "Pretty printed"


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = (
        "platform",
        "is_fb_log_enabled",
        "is_af_log_enabled",
        "is_adjust_log_enabled",
    )

    actions = [
        "enable_facebook_logging",
        "disable_facebook_logging",
        "enable_appsflyer_logging",
        "disable_appsflyer_logging",
        "enable_adjust_logging",
        "disable_adjust_logging",
    ]

    def disable_adjust_logging(self, request, queryset):
        self.message_user(
            request,
            "Adjust logging was successfully disabled.",
            messages.SUCCESS,
        )

    def disable_appsflyer_logging(self, request, queryset):
        self.message_user(
            request,
            "AppsFlyer logging was successfully disabled.",
            messages.SUCCESS,
        )

    def disable_facebook_logging(self, request, queryset):
        self.message_user(
            request,
            "Facebook logging was successfully disabled.",
            messages.SUCCESS,
        )

    def enable_adjust_logging(self, request, queryset):
        self.message_user(
            request,
            "Adjust logging was successfully enabled.",
            messages.SUCCESS,
        )

    def enable_appsflyer_logging(self, request, queryset):
        self.message_user(
            request,
            "AppsFlyer logging was successfully enabled.",
            messages.SUCCESS,
        )

    def enable_facebook_logging(self, request, queryset):
        self.message_user(
            request,
            "Facebook logging was successfully enabled.",
            messages.SUCCESS,
        )


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    readonly_fields = ("pretty_details",)
    list_display = (
        "log_time",
        "platform",
        "version",
        "log_level",
        "message",
    )
    list_filter = (
        ("time", DateTimeRangeFilter),
        "platform",
        "log_level",
        "message",
        "version",
    )

    def get_rangefilter_time_default(self, _request):
        return timezone.datetime.today, timezone.datetime.today

    def get_rangefilter_time_title(self, _request, _field_path):
        return "Date Filter"

    @staticmethod
    def log_time(obj):
        return obj.time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def pretty_details(obj):
        return pretty_printed(obj, "details")

    pretty_details.short_description = "details"


@admin.register(AdjustLog)
class AdjustLogAdmin(admin.ModelAdmin):
    list_display = (
        "get_transaction_id",
        "get_platform",
        "get_version",
        "request_data",
        "response",
        "created_at",
    )
    list_filter = (
        ("created_at", DateTimeRangeFilter),
        "purchase__platform",
        "purchase__bundle_short_version",
    )
    search_fields = ("purchase__transaction_id",)
    fieldsets = (
        (None, {"fields": ("purchase",)}),
        (
            "Request",
            {"fields": ("request_url", "request_headers_pp", "request_data_pp")},
        ),
        ("Response", {"fields": ("response_pp",)}),
    )

    readonly_fields = (
        "purchase",
        "request_headers_pp",
        "request_data_pp",
        "request_url",
        "response_pp",
    )

    def get_rangefilter_time_default(self, _request):
        return timezone.datetime.today, timezone.datetime.today

    def get_rangefilter_time_title(self, _request, _field_path):
        return "Date Filter"

    def get_platform(self, obj):
        return obj.purchase.platform.title()

    get_platform.short_description = "Platform"
    get_platform.admin_order_field = "purchase__platform"

    def get_version(self, obj):
        return obj.purchase.bundle_short_version

    get_version.short_description = "Version"
    get_version.admin_order_field = "purchase__bundle_short_version"

    def get_transaction_id(self, obj):
        return obj.purchase.transaction_id

    get_transaction_id.short_description = "Transaction id"
    get_transaction_id.admin_order_field = "purchase__transaction_id"

    def request_headers_pp(self, obj):
        return pretty_printed(obj, "request_headers")

    request_headers_pp.short_description = "Headers"

    def request_data_pp(self, obj):
        return pretty_printed(obj, "request_data")

    request_data_pp.short_description = "Body"

    def response_pp(self, obj):
        return pretty_printed(obj, "response")

    response_pp.short_description = "Data"


@admin.register(AppsFlyer)
class AppsFlyerAdmin(admin.ModelAdmin):
    list_display = ("platform", "app_id", "dev_key")
    fieldsets = (
        (None, {"fields": ("platform", )}),
        ("App", {"fields": ("app_id", "dev_key")}),
    )


@admin.register(Facebook)
class FacebookAdmin(admin.ModelAdmin):
    list_display = ("platform", "app_id", "client_secret")

    fieldsets = (
        (None, {"fields": ("platform", )}),
        ("App", {"fields": ("app_id", "client_secret")}),
    )


@admin.register(Google)
class GoogleAdmin(admin.ModelAdmin):
    list_display = (
        "type",
        "project_id",
        "json_action",
        "client_email",
    )
    list_filter = ("client_email",)

    fieldsets = (
        (None, {"fields": ("type", "project_id")}),
        ("keys", {"fields": ("private_key_id", "private_key")}),
        ("client credentials", {"fields": ("client_email", "client_id")}),
        ("auth uri", {"fields": ("auth_uri", "token_uri")}),
        ("certs", {"fields": ("auth_provider_x509_cert_url", "client_x509_cert_url")}),
    )

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.json_action_form = FileUploadForm

    def load_from_json(self, request, instance_id):
        return self.process_action(
            request=request,
            instance_id=instance_id,
            action_title=None,
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r"^(?P<instance_id>.+)/load-from-json/$",
                self.admin_site.admin_view(self.load_from_json),
                name="load-from-json",
            ),
        ]
        return custom_urls + urls

    def json_action(self, obj):
        return format_html(
            '<a class="button" href="{}">JSON</a>',
            reverse("admin:load-from-json", args=[obj.pk]),
        )

    json_action.short_description = "Load Values"
    json_action.allow_tags = True

    def process_action(self, request, instance_id, action_title):
        queryset = self.get_queryset(request).filter(pk=instance_id)
        if request.method != "POST":
            form = self.json_action_form()
        else:
            form, redirect = self.form_with_file_request(request, queryset, instance_id)
            if redirect is not None:
                return redirect
        context = self.admin_site.each_context(request)
        context["opts"] = self.model._meta
        context["form"] = form
        context["google"] = queryset
        context["title"] = action_title
        return TemplateResponse(
            request,
            "google_json_load_form.html",
            context,
        )

    def form_with_file_request(self, request, queryset, instance_id):
        form = self.json_action_form(request.POST, request.FILES)
        if form.is_valid():
            redirect_url = (
                f"/djadmin/{Google._meta.app_label}/{Google._meta.model_name}/"
            )
            try:
                form.save(queryset)
            except (ValidationError, IntegrityError) as e:
                messages.error(request, f"Database error: {e}")
                return form, HttpResponseRedirect(redirect_url)
            messages.success(request, "Success")
            return form, HttpResponseRedirect(f"{redirect_url}{instance_id}/")
        return (form, )


@admin.register(Adjust)
class AdjustAdmin(admin.ModelAdmin):
    list_display = (
        "platform",
        "app_token",
        "purchase_event_token",
        "authorization_token",
    )
