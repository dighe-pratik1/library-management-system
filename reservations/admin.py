from django.contrib import admin

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "member",
        "book",
        "book_copy",
        "reservation_date",
        "status",
        "ready_date",
        "fulfilled_date",
    )

    list_filter = (
        "status",
        "reservation_date",
        "ready_date",
    )

    search_fields = (
        "member__member_code",
        "member__first_name",
        "member__last_name",
        "book__title",
        "book__isbn",
        "book_copy__accession_number",
        "book_copy__barcode",
    )

    ordering = (
        "-reservation_date",
        "-id",
    )