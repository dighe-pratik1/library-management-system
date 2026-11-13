from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from members.models import Member
from books.models import Book, BookCopy


class Reservation(models.Model):

    class ReservationStatus(models.TextChoices):

        PENDING = "PENDING", "Pending"
        READY = "READY", "Ready"
        FULFILLED = "FULFILLED", "Fulfilled"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"

    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="reservations"
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="reservations"
    )

    # A copy is assigned only when the reservation becomes READY
    book_copy = models.ForeignKey(
        BookCopy,
        on_delete=models.PROTECT,
        related_name="reservation_records",
        null=True,
        blank=True
    )

    reservation_date = models.DateField(
        default=timezone.localdate
    )

    ready_date = models.DateField(
        null=True,
        blank=True
    )

    fulfilled_date = models.DateField(
        null=True,
        blank=True
    )

    cancelled_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "-reservation_date",
            "-id"
        ]

    def clean(self):

        # Member must be active
        if self.member_id:

            if not self.member.status:
                raise ValidationError(
                    "This member is inactive."
                )

        # Book must be active
        if self.book_id:

            if not self.book.status:
                raise ValidationError(
                    "This book is inactive."
                )

        # Book copy, if assigned, must belong to same book
        if self.book_copy_id and self.book_id:

            if self.book_copy.book_id != self.book_id:
                raise ValidationError(
                    "Selected book copy does not belong to this book."
                )

    def __str__(self):

        return (
            f"{self.member.member_code} - "
            f"{self.book.title} - "
            f"{self.status}"
        )