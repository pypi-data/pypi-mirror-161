from django.conf import settings
from django.contrib import admin

from . import models


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    """
    Admin for Person model
    """

    list_display = getattr(
        settings, "PEOPLE_ADMIN_LIST_DISPLAY", ["name", "job_role", "order", "is_published"],
    )
    search_fields = getattr(settings, "PEOPLE_ADMIN_SEARCH_FIELDS", ["name", "job_role"])
    list_editable = ["order"]
    readonly_fields = getattr(
        settings, "PEOPLE_ADMIN_READONLY_FIELDS", ["created_at", "updated_at",]
    )
    fieldsets = getattr(
        settings,
        "PEOPLE_ADMIN_FIELDSETS",
        (
            (None, {"fields": ["name", "job_role", "order", "image", "summary"]}),
            ("Contact", {"fields": ["email", "phone_number", "linkedin_url"]}),
            ("Publish", {"fields": ["is_published", "publish_at"]}),
            ("Meta Data", {"classes": ("collapse",), "fields": ["created_at", "updated_at"]},),
        ),
    )
