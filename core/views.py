from django.shortcuts import render
from django.apps import apps
from django.utils import timezone


def get_model(app_name, model_name):
    """
    Safely get an existing Django model.
    Returns None if the model does not exist.
    """
    try:
        return apps.get_model(app_name, model_name)
    except LookupError:
        return None


def get_count(app_name, model_name):
    """
    Safely count records from an existing model.
    """
    model = get_model(app_name, model_name)

    if model is None:
        return 0

    try:
        return model.objects.count()
    except Exception:
        return 0


def dashboard(request):

    # -----------------------------------------
    # TOTAL RECORDS
    # -----------------------------------------

    total_books = get_count("books", "Book")

    total_members = get_count("members", "Member")

    total_copies = get_count("books", "BookCopy")

    total_issues = get_count("members", "IssueRecord")


    # -----------------------------------------
    # ISSUE RECORD
    # -----------------------------------------

    IssueRecord = get_model(
        "members",
        "IssueRecord"
    )

    issued_books = 0
    overdue_books = 0
    recent_issues = []


    if IssueRecord is not None:

        # -------------------------------------
        # ISSUED BOOKS
        # -------------------------------------

        try:
            issued_books = IssueRecord.objects.filter(
                status="ISSUED"
            ).count()
        except Exception:
            issued_books = 0


        # -------------------------------------
        # OVERDUE BOOKS
        # -------------------------------------

        try:
            overdue_books = IssueRecord.objects.filter(
                status="OVERDUE"
            ).count()
        except Exception:

            # If OVERDUE status is not stored,
            # calculate overdue using due_date.

            try:

                overdue_books = IssueRecord.objects.filter(
                    due_date__lt=timezone.localdate(),
                    return_date__isnull=True
                ).count()

            except Exception:
                overdue_books = 0


        # -------------------------------------
        # RECENT ISSUES
        # -------------------------------------

        try:

            records = IssueRecord.objects.all().order_by(
                "-issue_date"
            )[:10]

        except Exception:

            try:
                records = IssueRecord.objects.all()[:10]
            except Exception:
                records = []


        for record in records:

            # Member
            member = getattr(
                record,
                "member",
                None
            )

            # Book copy
            book_copy = getattr(
                record,
                "book_copy",
                None
            )

            # Book
            book = None

            if book_copy is not None:
                book = getattr(
                    book_copy,
                    "book",
                    None
                )

            # Member name
            if member is not None:
                member_name = str(member)
            else:
                member_name = "-"

            # Book name
            if book is not None:
                book_name = str(book)
            elif book_copy is not None:
                book_name = str(book_copy)
            else:
                book_name = "-"

            recent_issues.append({

                "member": member_name,

                "book": book_name,

                "issue_date": getattr(
                    record,
                    "issue_date",
                    None
                ),

                "due_date": getattr(
                    record,
                    "due_date",
                    None
                ),

                "status": getattr(
                    record,
                    "status",
                    "-"
                ),

            })


    # -----------------------------------------
    # AVAILABLE BOOK COPIES
    # -----------------------------------------

    available_copies = 0

    BookCopy = get_model(
        "books",
        "BookCopy"
    )

    if BookCopy is not None:

        try:

            available_copies = BookCopy.objects.filter(
                status="AVAILABLE"
            ).count()

        except Exception:

            available_copies = 0


    # -----------------------------------------
    # DASHBOARD DATA
    # -----------------------------------------

    context = {

        "total_books": total_books,

        "total_members": total_members,

        "total_copies": total_copies,

        "available_copies": available_copies,

        "issued_books": issued_books,

        "overdue_books": overdue_books,

        "total_issues": total_issues,

        "recent_issues": recent_issues,

    }


    return render(
        request,
        "home.html",
        context
    )