from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "member",
        "fine",
        "amount",
        "payment_method",
        "transaction_id",
        "status",
        "payment_date",
    )

    list_filter = (
        "payment_method",
        "status",
        "payment_date",
    )

    search_fields = (
        "member__first_name",
        "member__last_name",
        "member__member_code",
        "transaction_id",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )