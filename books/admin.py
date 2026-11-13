from django.contrib import admin
from .models import Author, Publisher, Category, Book, BookCopy


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'country',
        'website',
        'status',
        'created_at',
    )

    search_fields = (
        'name',
        'country',
    )

    list_filter = (
        'status',
        'country',
    )


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'city',
        'state',
        'country',
        'phone',
        'email',
        'status',
        'created_at',
    )

    search_fields = (
        'name',
        'city',
        'state',
        'country',
        'phone',
        'email',
    )

    list_filter = (
        'status',
        'country',
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'code',
        'status',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'name',
        'code',
    )

    list_filter = (
        'status',
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'isbn',
        'author',
        'publisher',
        'category',
        'language',
        'price',
        'status',
        'created_at',
    )

    search_fields = (
        'title',
        'isbn',
        'author__name',
        'publisher__name',
    )

    list_filter = (
        'category',
        'publisher',
        'language',
        'status',
    )
@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):

    list_display = (
        'accession_number',
        'barcode',
        'book',
        'status',
        'shelf',
        'rack',
        'condition',
        'purchase_price',
    )

    search_fields = (
        'accession_number',
        'barcode',
        'book__title',
        'book__isbn',
    )

    list_filter = (
        'status',
        'condition',
    )