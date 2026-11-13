from django.db import models
from django.utils import timezone


class Notification(models.Model):

    # =====================================================
    # NOTIFICATION TYPES
    # =====================================================

    class NotificationType(models.TextChoices):

        GENERAL = "GENERAL", "General"

        ISSUE = "ISSUE", "Book Issued"

        RETURN = "RETURN", "Book Returned"

        DUE_SOON = "DUE_SOON", "Due Soon"

        OVERDUE = "OVERDUE", "Overdue"

        FINE = "FINE", "Fine"

        PAYMENT = "PAYMENT", "Payment"

        RESERVATION = "RESERVATION", "Reservation"

        MEMBERSHIP = "MEMBERSHIP", "Membership"


    # =====================================================
    # PRIORITY
    # =====================================================

    class Priority(models.TextChoices):

        LOW = "LOW", "Low"

        NORMAL = "NORMAL", "Normal"

        HIGH = "HIGH", "High"


    # =====================================================
    # MEMBER
    # =====================================================

    member = models.ForeignKey(
        "members.Member",
        on_delete=models.CASCADE,
        related_name="notifications"
    )


    # =====================================================
    # TITLE
    # =====================================================

    title = models.CharField(
        max_length=200
    )


    # =====================================================
    # MESSAGE
    # =====================================================

    message = models.TextField()


    # =====================================================
    # NOTIFICATION TYPE
    # =====================================================

    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL
    )


    # =====================================================
    # PRIORITY
    # =====================================================

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL
    )


    # =====================================================
    # READ / UNREAD
    # =====================================================

    is_read = models.BooleanField(
        default=False
    )


    # =====================================================
    # NOTIFICATION DATE
    # =====================================================

    notification_date = models.DateTimeField(
        default=timezone.now
    )


    # =====================================================
    # OPTIONAL LINK
    # =====================================================

    link = models.CharField(
        max_length=500,
        blank=True
    )


    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    # =====================================================
    # ORDERING
    # =====================================================

    class Meta:

        ordering = [
            "-notification_date",
            "-id"
        ]


    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):

        return (
            f"{self.member} - "
            f"{self.title}"
        )