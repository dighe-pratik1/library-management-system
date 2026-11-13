from django.db import models


# =========================================================
# AUTHOR
# =========================================================

class Author(models.Model):

    name = models.CharField(
        max_length=150
    )

    biography = models.TextField(
        blank=True
    )

    photo = models.ImageField(
        upload_to="authors/",
        blank=True,
        null=True
    )

    country = models.CharField(
        max_length=100,
        blank=True
    )

    website = models.URLField(
        blank=True
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


# =========================================================
# PUBLISHER
# =========================================================

class Publisher(models.Model):

    name = models.CharField(
        max_length=200,
        unique=True
    )

    description = models.TextField(
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

    country = models.CharField(
        max_length=100,
        blank=True
    )

    pincode = models.CharField(
        max_length=10,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    logo = models.ImageField(
        upload_to="publishers/",
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
        return self.name


# =========================================================
# CATEGORY
# =========================================================

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    code = models.CharField(
        max_length=20,
        unique=True
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


# =========================================================
# BOOK
# =========================================================

class Book(models.Model):

    title = models.CharField(
        max_length=250
    )

    # =====================================================
    # AUTOMATIC ISBN
    # =====================================================

    isbn = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name="books"
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.PROTECT,
        related_name="books"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="books"
    )

    description = models.TextField(
        blank=True
    )

    edition = models.CharField(
        max_length=50,
        blank=True
    )

    publication_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    language = models.CharField(
        max_length=50,
        default="English"
    )

    pages = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    cover_image = models.ImageField(
        upload_to="books/",
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

    # =====================================================
    # AUTOMATIC ISBN GENERATION
    # =====================================================

    def save(self, *args, **kwargs):

        # Generate ISBN only for a new/empty ISBN
        if not self.isbn:

            start_number = 1000000000001

            # Find previously generated numeric ISBN
            last_generated = (
                Book.objects
                .filter(
                    isbn__gte=str(start_number)
                )
                .order_by("-isbn")
                .first()
            )

            if last_generated:

                try:
                    next_number = (
                        int(last_generated.isbn) + 1
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    next_number = start_number

            else:

                next_number = start_number

            # Prevent duplicate ISBN
            while Book.objects.filter(
                isbn=str(next_number)
            ).exists():

                next_number += 1

            self.isbn = str(
                next_number
            )

        # Save Book
        super().save(
            *args,
            **kwargs
        )

    def __str__(self):
        return self.title


# =========================================================
# BOOK COPY
# =========================================================

class BookCopy(models.Model):

    class CopyStatus(models.TextChoices):

        AVAILABLE = (
            "AVAILABLE",
            "Available"
        )

        ISSUED = (
            "ISSUED",
            "Issued"
        )

        RESERVED = (
            "RESERVED",
            "Reserved"
        )

        DAMAGED = (
            "DAMAGED",
            "Damaged"
        )

        LOST = (
            "LOST",
            "Lost"
        )

        MAINTENANCE = (
            "MAINTENANCE",
            "Maintenance"
        )

    # =====================================================
    # BOOK
    # =====================================================

    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="copies"
    )

    # =====================================================
    # AUTOMATIC ACCESSION NUMBER
    # =====================================================

    accession_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    # =====================================================
    # AUTOMATIC BARCODE
    # =====================================================

    barcode = models.CharField(
        max_length=100,
        unique=True,
        blank=True
    )

    # =====================================================
    # STATUS
    # =====================================================

    status = models.CharField(
        max_length=20,
        choices=CopyStatus.choices,
        default=CopyStatus.AVAILABLE
    )

    # =====================================================
    # LOCATION
    # =====================================================

    shelf = models.CharField(
        max_length=50,
        blank=True
    )

    rack = models.CharField(
        max_length=50,
        blank=True
    )

    # =====================================================
    # PURCHASE DETAILS
    # =====================================================

    purchase_date = models.DateField(
        null=True,
        blank=True
    )

    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # =====================================================
    # CONDITION
    # =====================================================

    condition = models.CharField(
        max_length=50,
        default="Good"
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

    # =====================================================
    # AUTOMATIC ACCESSION + BARCODE
    # =====================================================

    def save(self, *args, **kwargs):

        # =================================================
        # GENERATE ACCESSION NUMBER
        # =================================================

        if not self.accession_number:

            next_number = 1

            # Get all existing accession numbers
            existing_numbers = []

            for value in (
                BookCopy.objects
                .exclude(
                    accession_number=""
                )
                .values_list(
                    "accession_number",
                    flat=True
                )
            ):

                if value.startswith("ACC-"):

                    try:

                        number = int(
                            value.replace(
                                "ACC-",
                                ""
                            )
                        )

                        existing_numbers.append(
                            number
                        )

                    except (
                        ValueError,
                        TypeError
                    ):

                        pass

            if existing_numbers:

                next_number = (
                    max(existing_numbers) + 1
                )

            # Make sure it is unique
            while BookCopy.objects.filter(
                accession_number=(
                    f"ACC-{next_number:04d}"
                )
            ).exists():

                next_number += 1

            self.accession_number = (
                f"ACC-{next_number:04d}"
            )

        # =================================================
        # GENERATE BARCODE
        # =================================================

        if not self.barcode:

            next_number = 1

            # Get all existing barcode numbers
            existing_barcode_numbers = []

            for value in (
                BookCopy.objects
                .exclude(
                    barcode=""
                )
                .values_list(
                    "barcode",
                    flat=True
                )
            ):

                if value.startswith("LIB"):

                    try:

                        number = int(
                            value.replace(
                                "LIB",
                                ""
                            )
                        )

                        existing_barcode_numbers.append(
                            number
                        )

                    except (
                        ValueError,
                        TypeError
                    ):

                        pass

            if existing_barcode_numbers:

                next_number = (
                    max(existing_barcode_numbers) + 1
                )

            # Make sure barcode is unique
            while BookCopy.objects.filter(
                barcode=(
                    f"LIB{next_number:09d}"
                )
            ).exists():

                next_number += 1

            self.barcode = (
                f"LIB{next_number:09d}"
            )

        # =================================================
        # SAVE BOOK COPY
        # =================================================

        super().save(
            *args,
            **kwargs
        )

    def __str__(self):

        return (
            f"{self.book.title} - "
            f"{self.accession_number}"
        )