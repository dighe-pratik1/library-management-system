from django.db import models


class Library(models.Model):

    name = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    code = models.CharField(
        max_length=50,
        unique=True
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
        default="India"
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
        upload_to="library_logos/",
        blank=True,
        null=True
    )

    opening_time = models.TimeField(
        blank=True,
        null=True
    )

    closing_time = models.TimeField(
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