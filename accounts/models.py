from django.db import models
from django.utils import timezone

class EmailOTP(models.Model):
    PURPOSE_CHOICES = [
        ("register", "Registration"),
        ("reset", "Password Reset"),
    ]
    email = models.EmailField(db_index=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"{self.email} - {self.purpose}"
