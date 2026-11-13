from django.contrib import admin

from .models import Fine


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "member",
        "issue_record",
        "amount",
        "paid_amount",
        "balance",
        "status",
        "fine_date",
        "paid_date",
    )

    list_filter = (
        "status",
        "fine_date",
        "paid_date",
    )

    search_fields = (
        "member__first_name",
        "member__last_name",
        "member__member_code",
    )

    readonly_fields = (
        "balance",
        "created_at",
        "updated_at",
    )