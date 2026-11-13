from django.contrib import admin
from .models import EmailOTP

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("email", "purpose", "expires_at", "attempts", "created_at")
    list_filter = ("purpose",)
    search_fields = ("email",)
    readonly_fields = ("code_hash", "created_at")
