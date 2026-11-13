from decimal import Decimal

from django.db import models
from django.utils import timezone


class Fine(models.Model):

    class FineStatus(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PARTIAL = "PARTIAL", "Partially Paid"
        PAID = "PAID", "Paid"

    # Issue record related to this fine
    issue_record = models.OneToOneField(
        "members.IssueRecord",
        on_delete=models.PROTECT,
        related_name="fine",
        null=True,
        blank=True
    )

    # Member
    member = models.ForeignKey(
        "members.Member",
        on_delete=models.PROTECT,
        related_name="fines"
    )

    # Fine amount
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    # Amount already paid
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    # Remaining balance
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    # Fine status
    status = models.CharField(
        max_length=20,
        choices=FineStatus.choices,
        default=FineStatus.UNPAID
    )

    # Reason
    reason = models.CharField(
        max_length=255,
        default="Late return"
    )

    # Fine date
    fine_date = models.DateField(
        default=timezone.localdate
    )

    # Payment date
    paid_date = models.DateField(
        null=True,
        blank=True
    )

    # Notes
    notes = models.TextField(
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # =====================================================
    # CALCULATE BALANCE AND STATUS
    # =====================================================
    def calculate_balance(self):

        self.amount = Decimal(
            str(self.amount or 0)
        )

        self.paid_amount = Decimal(
            str(self.paid_amount or 0)
        )

        # Prevent paid amount from being greater than fine
        if self.paid_amount > self.amount:
            self.paid_amount = self.amount

        # Calculate balance
        self.balance = max(
            Decimal("0.00"),
            self.amount - self.paid_amount
        )

        # Determine status
        if self.paid_amount <= Decimal("0.00"):

            self.status = self.FineStatus.UNPAID

            self.paid_date = None

        elif self.paid_amount < self.amount:

            self.status = self.FineStatus.PARTIAL

            self.paid_date = None

        else:

            self.status = self.FineStatus.PAID

            if not self.paid_date:
                self.paid_date = timezone.localdate()

    # =====================================================
    # SAVE
    # =====================================================
    def save(self, *args, **kwargs):

        self.calculate_balance()

        super().save(
            *args,
            **kwargs
        )

    # =====================================================
    # STRING
    # =====================================================
    def __str__(self):

        return (
            f"{self.member} - "
            f"₹{self.amount} - "
            f"{self.status}"
        )