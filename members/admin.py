from django.contrib import admin
from .models import MembershipType, Member, IssueRecord


@admin.register(MembershipType)
class MembershipTypeAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'max_books',
        'loan_days',
        'renewal_limit',
        'fine_per_day',
        'membership_fee',
        'status',
    )

    search_fields = (
        'name',
    )

    list_filter = (
        'status',
    )


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):

    list_display = (
        'member_code',
        'first_name',
        'last_name',
        'mobile',
        'membership_type',
        'department',
        'course',
        'status',
    )

    search_fields = (
        'member_code',
        'first_name',
        'last_name',
        'mobile',
        'email',
        'roll_number',
    )

    list_filter = (
        'membership_type',
        'department',
        'status',
    )
@admin.register(IssueRecord)
class IssueRecordAdmin(admin.ModelAdmin):

    list_display = (
        'member',
        'book_copy',
        'issue_date',
        'due_date',
        'return_date',
        'status',
        'fine_amount',
    )

    search_fields = (
        'member__name',
        'book_copy__accession_number',
        'book_copy__barcode',
        'book_copy__book__title',
    )

    list_filter = (
        'status',
        'issue_date',
        'due_date',
    )

    date_hierarchy = 'issue_date'