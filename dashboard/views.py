from django.shortcuts import render

from books.models import Book, BookCopy, Author, Publisher, Category
from members.models import Member


def home(request):

    total_books = Book.objects.count()
    total_copies = BookCopy.objects.count()
    total_authors = Author.objects.count()
    total_publishers = Publisher.objects.count()
    total_categories = Category.objects.count()
    total_members = Member.objects.count()

    available_copies = BookCopy.objects.filter(
        status="AVAILABLE"
    ).count()

    issued_copies = BookCopy.objects.filter(
        status="ISSUED"
    ).count()

    return render(
        request,
        "dashboard/home.html",
        {
            "total_books": total_books,
            "total_copies": total_copies,
            "total_authors": total_authors,
            "total_publishers": total_publishers,
            "total_categories": total_categories,
            "total_members": total_members,
            "available_copies": available_copies,
            "issued_copies": issued_copies,
        }
    )