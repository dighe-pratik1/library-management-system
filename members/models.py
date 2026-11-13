from datetime import timedelta, datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


# ==========================================================
# MEMBERSHIP TYPE
# ==========================================================

class MembershipType(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    max_books = models.PositiveIntegerField(
        default=3
    )

    loan_days = models.PositiveIntegerField(
        default=14
    )

    renewal_limit = models.PositiveIntegerField(
        default=2
    )

    fine_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=2.00
    )

    membership_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    status = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


# ==========================================================
# MEMBER
# ==========================================================

class Member(models.Model):

    member_code = models.CharField(
        max_length=50,
        unique=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100,
        blank=True
    )

    gender = models.CharField(
        max_length=20,
        choices=[
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other"),
        ],
        blank=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    mobile = models.CharField(
        max_length=20
    )

    email = models.EmailField(
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    pincode = models.CharField(
        max_length=10,
        blank=True
    )

    photo = models.ImageField(
        upload_to="members/",
        blank=True,
        null=True
    )

    membership_type = models.ForeignKey(
        MembershipType,
        on_delete=models.PROTECT,
        related_name="members"
    )

    department = models.CharField(
        max_length=100,
        blank=True
    )

    course = models.CharField(
        max_length=100,
        blank=True
    )

    year = models.CharField(
        max_length=20,
        blank=True
    )

    roll_number = models.CharField(
        max_length=50,
        blank=True
    )

    joining_date = models.DateField(
        auto_now_add=True
    )

    expiry_date = models.DateField(
        blank=True,
        null=True
    )

    status = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return (
            f"{self.member_code} - "
            f"{self.first_name} "
            f"{self.last_name}"
        )


# ==========================================================
# ISSUE RECORD
# ==========================================================

class IssueRecord(models.Model):

    class IssueStatus(models.TextChoices):

        ISSUED = "ISSUED", "Issued"

        RETURNED = "RETURNED", "Returned"

        OVERDUE = "OVERDUE", "Overdue"

        LOST = "LOST", "Lost"


    # ======================================================
    # MEMBER
    # ======================================================

    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="issue_records"
    )


    # ======================================================
    # BOOK COPY
    # ======================================================

    book_copy = models.ForeignKey(
        "books.BookCopy",
        on_delete=models.PROTECT,
        related_name="issue_records"
    )


    # ======================================================
    # ISSUE DATE
    # ======================================================

    issue_date = models.DateField()


    # ======================================================
    # DUE DATE
    # ======================================================

    due_date = models.DateField(
        null=True,
        blank=True
    )


    # ======================================================
    # RETURN DATE
    # ======================================================

    return_date = models.DateField(
        null=True,
        blank=True
    )


    # ======================================================
    # STATUS
    # ======================================================

    status = models.CharField(
        max_length=20,
        choices=IssueStatus.choices,
        default=IssueStatus.ISSUED
    )


    # ======================================================
    # FINE
    # ======================================================

    fine_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )


    # ======================================================
    # NOTES
    # ======================================================

    notes = models.TextField(
        blank=True
    )


    # ======================================================
    # CREATED / UPDATED
    # ======================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    # ======================================================
    # CONVERT DATE
    # ======================================================

    @staticmethod
    def convert_to_date(value):

        # Already a date object
        if isinstance(value, datetime):
            return value.date()

        if hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day"):
            return value

        # Convert HTML date string
        if isinstance(value, str):

            value = value.strip()

            if not value:
                return None

            try:
                return datetime.strptime(
                    value,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                raise ValidationError(
                    "Invalid date format. Please use YYYY-MM-DD."
                )

        return value


    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        # Convert dates before validation
        self.issue_date = self.convert_to_date(
            self.issue_date
        )

        self.due_date = self.convert_to_date(
            self.due_date
        )

        self.return_date = self.convert_to_date(
            self.return_date
        )


        # Issue date required
        if not self.issue_date:

            raise ValidationError(
                "Issue date is required."
            )


        # Due date cannot be before issue date
        if self.due_date and self.due_date < self.issue_date:

            raise ValidationError(
                "Due date cannot be before issue date."
            )


        # Return date cannot be before issue date
        if self.return_date and self.return_date < self.issue_date:

            raise ValidationError(
                "Return date cannot be before issue date."
            )


        # --------------------------------------------------
        # CHECK DUPLICATE ACTIVE ISSUE
        # --------------------------------------------------

        if self.status == self.IssueStatus.ISSUED:

            existing_issue = (
                IssueRecord.objects
                .filter(
                    book_copy=self.book_copy,
                    status=self.IssueStatus.ISSUED
                )
                .exclude(
                    pk=self.pk
                )
                .exists()
            )

            if existing_issue:

                raise ValidationError(
                    "This book copy is already issued."
                )


    # ======================================================
    # CALCULATE FINE
    # ======================================================

    def calculate_fine(self):

        # Convert dates safely
        due_date = self.convert_to_date(
            self.due_date
        )

        return_date = self.convert_to_date(
            self.return_date
        )


        # No due date
        if not due_date:
            return Decimal("0.00")


        # No return date
        if not return_date:
            return Decimal("0.00")


        # Returned on or before due date
        if return_date <= due_date:
            return Decimal("0.00")


        # Calculate overdue days
        overdue_days = (
            return_date - due_date
        ).days


        # Membership fine
        fine_per_day = (
            self.member
            .membership_type
            .fine_per_day
        )


        # Final fine
        return (
            Decimal(overdue_days)
            * fine_per_day
        )


    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        # --------------------------------------------------
        # CONVERT ISSUE DATE
        # --------------------------------------------------

        self.issue_date = self.convert_to_date(
            self.issue_date
        )


        # --------------------------------------------------
        # CONVERT DUE DATE
        # --------------------------------------------------

        self.due_date = self.convert_to_date(
            self.due_date
        )


        # --------------------------------------------------
        # CONVERT RETURN DATE
        # --------------------------------------------------

        self.return_date = self.convert_to_date(
            self.return_date
        )


        # --------------------------------------------------
        # ISSUE DATE REQUIRED
        # --------------------------------------------------

        if not self.issue_date:

            raise ValidationError(
                "Issue date is required."
            )


        # --------------------------------------------------
        # AUTOMATIC DUE DATE
        # --------------------------------------------------

        if not self.due_date:

            loan_days = (
                self.member
                .membership_type
                .loan_days
            )

            self.due_date = (
                self.issue_date
                + timedelta(
                    days=loan_days
                )
            )


        # --------------------------------------------------
        # AUTOMATIC FINE
        # --------------------------------------------------

        if self.status == self.IssueStatus.RETURNED:

            self.fine_amount = (
                self.calculate_fine()
            )

        else:

            self.fine_amount = Decimal(
                "0.00"
            )


        # --------------------------------------------------
        # AUTOMATIC OVERDUE STATUS
        # --------------------------------------------------

        if (
            self.status == self.IssueStatus.ISSUED
            and self.due_date
            and not self.return_date
        ):

            from datetime import date

            if date.today() > self.due_date:

                self.status = (
                    self.IssueStatus.OVERDUE
                )


        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        self.full_clean()


        # --------------------------------------------------
        # SAVE DATABASE RECORD
        # --------------------------------------------------

        super().save(
            *args,
            **kwargs
        )


        # --------------------------------------------------
        # UPDATE BOOK COPY STATUS
        # --------------------------------------------------

        if self.status in [
            self.IssueStatus.ISSUED,
            self.IssueStatus.OVERDUE
        ]:

            self.book_copy.status = "ISSUED"

            self.book_copy.save(
                update_fields=[
                    "status",
                    "updated_at"
                ]
            )


        elif self.status == self.IssueStatus.RETURNED:

            self.book_copy.status = "AVAILABLE"

            self.book_copy.save(
                update_fields=[
                    "status",
                    "updated_at"
                ]
            )


        elif self.status == self.IssueStatus.LOST:

            self.book_copy.status = "LOST"

            self.book_copy.save(
                update_fields=[
                    "status",
                    "updated_at"
                ]
            )


    # ======================================================
    # STRING
    # ======================================================

    def __str__(self):

        return (
            f"{self.member} - "
            f"{self.book_copy}"
        )