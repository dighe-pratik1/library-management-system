from django.contrib import admin
from .models import Library


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'code',
        'city',
        'state',
        'phone',
        'email',
        'status',
    )

    search_fields = (
        'name',
        'code',
        'city',
        'email',
    )

    list_filter = (
        'status',
        'state',
        'city',
    )