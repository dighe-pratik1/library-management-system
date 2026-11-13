from decimal import Decimal

from django.db import models
from django.utils import timezone


class Payment(models.Model):

    class PaymentMethod(models.TextChoices):

        CASH = "CASH", "Cash"
        UPI = "UPI", "UPI"
        CARD = "CARD", "Card"
        NET_BANKING = "NET_BANKING", "Net Banking"
        OTHER = "OTHER", "Other"

    class PaymentStatus(models.TextChoices):

        SUCCESS = "SUCCESS", "Success"
        PENDING = "PENDING", "Pending"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    # =====================================================
    # FINE
    # =====================================================

    fine = models.ForeignKey(
        "fines.Fine",
        on_delete=models.PROTECT,
        related_name="payments"
    )

    # =====================================================
    # MEMBER
    # =====================================================

    member = models.ForeignKey(
        "members.Member",
        on_delete=models.PROTECT,
        related_name="payments"
    )

    # =====================================================
    # PAYMENT AMOUNT
    # =====================================================

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    # =====================================================
    # PAYMENT METHOD
    # =====================================================

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )

    # =====================================================
    # TRANSACTION ID
    # =====================================================

    transaction_id = models.CharField(
        max_length=100,
        blank=True
    )

    # =====================================================
    # PAYMENT STATUS
    # =====================================================

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.SUCCESS
    )

    # =====================================================
    # PAYMENT DATE
    # =====================================================

    payment_date = models.DateField(
        default=timezone.localdate
    )

    # =====================================================
    # NOTES
    # =====================================================

    notes = models.TextField(
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
    # STRING
    # =====================================================

    def __str__(self):

        return (
            f"Payment #{self.id} - "
            f"{self.member} - "
            f"₹{self.amount}"
        )