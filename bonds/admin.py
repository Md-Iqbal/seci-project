from django.contrib import admin
from .models import *


@admin.register(WageEarnersBond)
class WageEarnersBondAdmin(admin.ModelAdmin):

    list_display = (
        "application_no",
        "applicant_name",
        "face_value",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "application_date",
    )

    search_fields = (
        "application_no",
        "passport_no",
        "applicant_name",
    )

    readonly_fields = (
        "application_no",
        "created_at",
        "updated_at",
    )
@admin.register(USDBond)
class USDBondAdmin(admin.ModelAdmin):

    list_display = (
        "application_no",
        "applicant_name",
        "face_value",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "application_date",
    )

    search_fields = (
        "application_no",
        "passport_no",
        "applicant_name",
    )

    readonly_fields = (
        "application_no",
        "created_at",
        "updated_at",
    )

admin.site.register(BondApprovalLog)
admin.site.register(USDBondApprovalLog)