from decimal import Decimal
from datetime import datetime

from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.utils import timezone

from books.models import Book, BookCopy
from members.models import Member, IssueRecord
from fines.models import Fine
from payments.models import Payment


def reports_home(request):
    """
    Main Reports Dashboard
    """

    # ---------------------------------------------------------
    # BASIC BOOK STATISTICS
    # ---------------------------------------------------------

    total_books = Book.objects.count()
    total_copies = BookCopy.objects.count()

    available_books = BookCopy.objects.filter(
        status=BookCopy.CopyStatus.AVAILABLE
    ).count()

    issued_books = BookCopy.objects.filter(
        status=BookCopy.CopyStatus.ISSUED
    ).count()

    reserved_books = BookCopy.objects.filter(
        status=BookCopy.CopyStatus.RESERVED
    ).count()

    lost_books = BookCopy.objects.filter(
        status=BookCopy.CopyStatus.LOST
    ).count()

    damaged_books = BookCopy.objects.filter(
        condition__iexact="Damaged"
    ).count()

    # ---------------------------------------------------------
    # BOOK PRICE
    # ---------------------------------------------------------

    book_price_result = Book.objects.aggregate(
        total=Sum("price")
    )

    total_book_price = book_price_result["total"] or Decimal("0.00")

    # Purchase value of all physical copies
    purchase_result = BookCopy.objects.aggregate(
        total=Sum("purchase_price")
    )

    total_purchase_value = purchase_result["total"] or Decimal("0.00")

    # ---------------------------------------------------------
    # STUDENT / MEMBER STATISTICS
    # ---------------------------------------------------------

    total_students = Member.objects.count()

    active_students = Member.objects.filter(
        status=True
    ).count()

    inactive_students = Member.objects.filter(
        status=False
    ).count()

    # ---------------------------------------------------------
    # ISSUE STATISTICS
    # ---------------------------------------------------------

    total_issue_records = IssueRecord.objects.count()

    currently_issued = IssueRecord.objects.filter(
        status=IssueRecord.IssueStatus.ISSUED
    ).count()

    returned_books = IssueRecord.objects.filter(
        status=IssueRecord.IssueStatus.RETURNED
    ).count()

    overdue_books = IssueRecord.objects.filter(
        status=IssueRecord.IssueStatus.ISSUED,
        due_date__lt=timezone.localdate()
    ).count()

    lost_issue_records = IssueRecord.objects.filter(
        status=IssueRecord.IssueStatus.LOST
    ).count()

    # ---------------------------------------------------------
    # FINE STATISTICS
    # ---------------------------------------------------------

    fine_result = Fine.objects.aggregate(
        total=Sum("amount"),
        paid=Sum("paid_amount"),
        balance=Sum("balance")
    )

    total_fine = fine_result["total"] or Decimal("0.00")
    total_fine_collected = fine_result["paid"] or Decimal("0.00")
    total_fine_due = fine_result["balance"] or Decimal("0.00")

    unpaid_fines = Fine.objects.filter(
        status=Fine.FineStatus.UNPAID
    ).count()

    partial_fines = Fine.objects.filter(
        status=Fine.FineStatus.PARTIAL
    ).count()

    paid_fines = Fine.objects.filter(
        status=Fine.FineStatus.PAID
    ).count()

    # ---------------------------------------------------------
    # PAYMENT STATISTICS
    # ---------------------------------------------------------

    payment_result = Payment.objects.filter(
        status=Payment.PaymentStatus.SUCCESS
    ).aggregate(
        total=Sum("amount")
    )

    total_payment_collection = (
        payment_result["total"] or Decimal("0.00")
    )

    total_payments = Payment.objects.count()

    successful_payments = Payment.objects.filter(
        status=Payment.PaymentStatus.SUCCESS
    ).count()

    # ---------------------------------------------------------
    # RECENT ISSUE RECORDS
    # ---------------------------------------------------------

    recent_issues = IssueRecord.objects.select_related(
        "member",
        "book_copy",
        "book_copy__book"
    ).order_by("-issue_date", "-id")[:10]

    # ---------------------------------------------------------
    # RECENT STUDENTS
    # ---------------------------------------------------------

    recent_students = Member.objects.select_related(
        "membership_type"
    ).order_by("-id")[:10]

    # ---------------------------------------------------------
    # RECENT PAYMENTS
    # ---------------------------------------------------------

    recent_payments = Payment.objects.select_related(
        "member",
        "fine",
        "fine__issue_record",
        "fine__issue_record__book_copy",
        "fine__issue_record__book_copy__book"
    ).order_by("-payment_date", "-id")[:10]

    # ---------------------------------------------------------
    # BOOK INVENTORY
    # ---------------------------------------------------------

    book_inventory = Book.objects.select_related(
        "author",
        "publisher",
        "category"
    ).annotate(
        copy_count=Count("copies"),
        available_count=Count(
            "copies",
            filter=Q(
                copies__status=BookCopy.CopyStatus.AVAILABLE
            )
        ),
        issued_count=Count(
            "copies",
            filter=Q(
                copies__status=BookCopy.CopyStatus.ISSUED
            )
        )
    ).order_by("title")

    # ---------------------------------------------------------
    # STUDENT SEARCH
    # ---------------------------------------------------------

    student_query = request.GET.get("student", "").strip()

    students = Member.objects.select_related(
        "membership_type"
    ).order_by("first_name", "last_name")

    if student_query:
        students = students.filter(
            Q(member_code__icontains=student_query)
            | Q(first_name__icontains=student_query)
            | Q(last_name__icontains=student_query)
            | Q(email__icontains=student_query)
            | Q(mobile__icontains=student_query)
        )

    # ---------------------------------------------------------
    # ISSUE SEARCH
    # ---------------------------------------------------------

    issue_query = request.GET.get("issue", "").strip()

    issue_records = IssueRecord.objects.select_related(
        "member",
        "book_copy",
        "book_copy__book"
    ).order_by("-issue_date", "-id")

    if issue_query:
        issue_records = issue_records.filter(
            Q(member__member_code__icontains=issue_query)
            | Q(member__first_name__icontains=issue_query)
            | Q(member__last_name__icontains=issue_query)
            | Q(book_copy__book__title__icontains=issue_query)
            | Q(book_copy__accession_number__icontains=issue_query)
            | Q(book_copy__barcode__icontains=issue_query)
        )

    # ---------------------------------------------------------
    # DATE FILTER
    # ---------------------------------------------------------

    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    if date_from:
        try:
            parsed_from = datetime.strptime(
                date_from, "%Y-%m-%d"
            ).date()

            issue_records = issue_records.filter(
                issue_date__gte=parsed_from
            )
        except ValueError:
            pass

    if date_to:
        try:
            parsed_to = datetime.strptime(
                date_to, "%Y-%m-%d"
            ).date()

            issue_records = issue_records.filter(
                issue_date__lte=parsed_to
            )
        except ValueError:
            pass

    # ---------------------------------------------------------
    # FINE RECORDS
    # ---------------------------------------------------------

    fine_records = Fine.objects.select_related(
        "member",
        "issue_record",
        "issue_record__book_copy",
        "issue_record__book_copy__book"
    ).order_by("-fine_date", "-id")

    # ---------------------------------------------------------
    # PAYMENT RECORDS
    # ---------------------------------------------------------

    payment_records = Payment.objects.select_related(
        "member",
        "fine",
        "fine__issue_record",
        "fine__issue_record__book_copy",
        "fine__issue_record__book_copy__book"
    ).order_by("-payment_date", "-id")

    # ---------------------------------------------------------
    # CONTEXT
    # ---------------------------------------------------------

    context = {

        # Dashboard statistics
        "total_books": total_books,
        "total_copies": total_copies,
        "available_books": available_books,
        "issued_books": issued_books,
        "reserved_books": reserved_books,
        "lost_books": lost_books,
        "damaged_books": damaged_books,

        # Money
        "total_book_price": total_book_price,
        "total_purchase_value": total_purchase_value,

        # Students
        "total_students": total_students,
        "active_students": active_students,
        "inactive_students": inactive_students,

        # Issues
        "total_issue_records": total_issue_records,
        "currently_issued": currently_issued,
        "returned_books": returned_books,
        "overdue_books": overdue_books,
        "lost_issue_records": lost_issue_records,

        # Fines
        "total_fine": total_fine,
        "total_fine_collected": total_fine_collected,
        "total_fine_due": total_fine_due,
        "unpaid_fines": unpaid_fines,
        "partial_fines": partial_fines,
        "paid_fines": paid_fines,

        # Payments
        "total_payment_collection": total_payment_collection,
        "total_payments": total_payments,
        "successful_payments": successful_payments,

        # Tables
        "recent_issues": recent_issues,
        "recent_students": recent_students,
        "recent_payments": recent_payments,
        "book_inventory": book_inventory,

        # Full records
        "students": students,
        "issue_records": issue_records,
        "fine_records": fine_records,
        "payment_records": payment_records,

        # Search/filter values
        "student_query": student_query,
        "issue_query": issue_query,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render(
        request,
        "reports/reports_home.html",
        context
    )