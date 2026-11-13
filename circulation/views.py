from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from members.models import Member, IssueRecord
from books.models import BookCopy
from reservations.models import Reservation


# =========================================================
# CIRCULATION HOME
# =========================================================

def circulation_home(request):

    total_issued = IssueRecord.objects.filter(
        status=IssueRecord.IssueStatus.ISSUED
    ).count()

    total_returned = IssueRecord.objects.filter(
        status=IssueRecord.IssueStatus.RETURNED
    ).count()

    total_overdue = IssueRecord.objects.filter(
        status=IssueRecord.IssueStatus.ISSUED,
        due_date__lt=timezone.localdate()
    ).count()

    available_copies = BookCopy.objects.filter(
        status=BookCopy.CopyStatus.AVAILABLE
    ).count()

    context = {
        "total_issued": total_issued,
        "total_returned": total_returned,
        "total_overdue": total_overdue,
        "available_copies": available_copies,
    }

    return render(
        request,
        "circulation/circulation_home.html",
        context
    )


# =========================================================
# ISSUE LIST
# =========================================================

def issue_list(request):

    search = request.GET.get(
        "search",
        ""
    ).strip()

    issues = IssueRecord.objects.select_related(
        "member",
        "member__membership_type",
        "book_copy",
        "book_copy__book"
    ).all().order_by(
        "-issue_date",
        "-id"
    )

    if search:

        issues = issues.filter(

            Q(member__member_code__icontains=search) |

            Q(member__first_name__icontains=search) |

            Q(member__last_name__icontains=search) |

            Q(book_copy__accession_number__icontains=search) |

            Q(book_copy__barcode__icontains=search) |

            Q(book_copy__book__title__icontains=search)
        )

    context = {
        "issues": issues,
        "search": search,
    }

    return render(
        request,
        "circulation/issue_list.html",
        context
    )


# =========================================================
# ISSUE BOOK
# =========================================================

def issue_book(request):

    # -----------------------------------------------------
    # ACTIVE MEMBERS
    # -----------------------------------------------------

    members = Member.objects.filter(
        status=True
    ).select_related(
        "membership_type"
    ).order_by(
        "first_name",
        "last_name"
    )

    # -----------------------------------------------------
    # AVAILABLE BOOK COPIES
    # -----------------------------------------------------

    copies = BookCopy.objects.filter(
        status=BookCopy.CopyStatus.AVAILABLE,
        book__status=True
    ).select_related(
        "book"
    ).order_by(
        "book__title",
        "accession_number"
    )

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        member_id = request.POST.get(
            "member"
        )

        book_copy_id = request.POST.get(
            "book_copy"
        )

        issue_date_text = request.POST.get(
            "issue_date"
        )

        notes = request.POST.get(
            "notes",
            ""
        ).strip()

        # -------------------------------------------------
        # MEMBER VALIDATION
        # -------------------------------------------------

        if not member_id:

            messages.error(
                request,
                "Please select a member."
            )

            return render(
                request,
                "circulation/issue_form.html",
                {
                    "members": members,
                    "copies": copies,
                    "today": timezone.localdate(),
                }
            )

        # -------------------------------------------------
        # BOOK COPY VALIDATION
        # -------------------------------------------------

        if not book_copy_id:

            messages.error(
                request,
                "Please select an available book."
            )

            return render(
                request,
                "circulation/issue_form.html",
                {
                    "members": members,
                    "copies": copies,
                    "today": timezone.localdate(),
                }
            )

        # -------------------------------------------------
        # GET MEMBER
        # -------------------------------------------------

        member = get_object_or_404(
            Member.objects.select_related(
                "membership_type"
            ),
            pk=member_id,
            status=True
        )

        # -------------------------------------------------
        # GET BOOK COPY
        # -------------------------------------------------

        book_copy = get_object_or_404(
            BookCopy.objects.select_related(
                "book"
            ),
            pk=book_copy_id
        )

        # -------------------------------------------------
        # ISSUE DATE
        # -------------------------------------------------

        if issue_date_text:

            try:

                issue_date = datetime.strptime(
                    issue_date_text,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                messages.error(
                    request,
                    "Invalid issue date."
                )

                return render(
                    request,
                    "circulation/issue_form.html",
                    {
                        "members": members,
                        "copies": copies,
                        "today": timezone.localdate(),
                    }
                )

        else:

            issue_date = timezone.localdate()

        # -------------------------------------------------
        # CHECK COPY STATUS
        # -------------------------------------------------

        if book_copy.status != BookCopy.CopyStatus.AVAILABLE:

            messages.error(
                request,
                "This book copy is no longer available."
            )

            return redirect(
                "issue_book"
            )

        # -------------------------------------------------
        # CHECK MEMBER BOOK LIMIT
        # -----------------------------------------------------

        current_books = IssueRecord.objects.filter(
            member=member,
            status=IssueRecord.IssueStatus.ISSUED
        ).count()

        max_books = member.membership_type.max_books

        if current_books >= max_books:

            messages.error(
                request,
                f"{member.first_name} has already reached "
                f"the maximum limit of {max_books} books."
            )

            return render(
                request,
                "circulation/issue_form.html",
                {
                    "members": members,
                    "copies": copies,
                    "today": timezone.localdate(),
                }
            )

        # -------------------------------------------------
        # CREATE ISSUE
        # -------------------------------------------------

        try:

            with transaction.atomic():

                issue = IssueRecord(
                    member=member,
                    book_copy=book_copy,
                    issue_date=issue_date,
                    status=IssueRecord.IssueStatus.ISSUED,
                    fine_amount=Decimal("0.00"),
                    notes=notes
                )

                issue.save()

            messages.success(
                request,
                f"'{book_copy.book.title}' issued successfully "
                f"to {member.first_name} {member.last_name}."
            )

            return redirect(
                "issue_list"
            )

        except ValidationError as e:

            messages.error(
                request,
                f"Cannot issue book: {e}"
            )

        except IntegrityError:

            messages.error(
                request,
                "This book copy could not be issued. "
                "It may already be issued."
            )

        except Exception as e:

            messages.error(
                request,
                f"Error while issuing book: {e}"
            )

    # -----------------------------------------------------
    # SHOW FORM
    # -----------------------------------------------------

    context = {
        "members": members,
        "copies": copies,
        "today": timezone.localdate(),
    }

    return render(
        request,
        "circulation/issue_form.html",
        context
    )


# =========================================================
# RETURN BOOK
# =========================================================

def return_book(request, pk):

    # -----------------------------------------------------
    # GET ISSUE RECORD
    # -----------------------------------------------------

    issue = get_object_or_404(

        IssueRecord.objects.select_related(

            "member",
            "member__membership_type",
            "book_copy",
            "book_copy__book"

        ),

        pk=pk
    )

    # -----------------------------------------------------
    # ALREADY RETURNED
    # -----------------------------------------------------

    if issue.status == IssueRecord.IssueStatus.RETURNED:

        messages.warning(
            request,
            "This book has already been returned."
        )

        return redirect(
            "issue_list"
        )

    # -----------------------------------------------------
    # POST = CONFIRM RETURN
    # -----------------------------------------------------

    if request.method == "POST":

        return_date_text = request.POST.get(
            "return_date"
        )

        # -------------------------------------------------
        # RETURN DATE
        # -------------------------------------------------

        if return_date_text:

            try:

                return_date = datetime.strptime(
                    return_date_text,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                messages.error(
                    request,
                    "Invalid return date."
                )

                return redirect(
                    "return_book",
                    pk=pk
                )

        else:

            return_date = timezone.localdate()

        # -------------------------------------------------
        # VALIDATE RETURN DATE
        # -------------------------------------------------

        if issue.issue_date and return_date < issue.issue_date:

            messages.error(
                request,
                "Return date cannot be before issue date."
            )

            return redirect(
                "return_book",
                pk=pk
            )

        # -------------------------------------------------
        # RETURN BOOK
        # -------------------------------------------------

        try:

            with transaction.atomic():

                # -----------------------------------------
                # Lock issue record
                # -----------------------------------------

                issue = (
                    IssueRecord.objects
                    .select_for_update()
                    .select_related(
                        "member",
                        "member__membership_type",
                        "book_copy",
                        "book_copy__book"
                    )
                    .get(pk=pk)
                )

                # -----------------------------------------
                # Check again
                # -----------------------------------------

                if issue.status == IssueRecord.IssueStatus.RETURNED:

                    messages.warning(
                        request,
                        "This book has already been returned."
                    )

                    return redirect(
                        "issue_list"
                    )

                # -----------------------------------------
                # Set return details
                # -----------------------------------------

                issue.return_date = return_date

                issue.status = (
                    IssueRecord.IssueStatus.RETURNED
                )

                # -----------------------------------------
                # IssueRecord.save()
                #
                # This calculates:
                # 1. Fine
                # 2. Due date
                # 3. BookCopy status
                # -----------------------------------------

                issue.save()

                # -----------------------------------------
                # RESERVATION INTEGRATION
                # -----------------------------------------

                reservation = (
                    assign_returned_copy_to_reservation(
                        issue.book_copy
                    )
                )

            # -------------------------------------------------
            # SUCCESS MESSAGE
            # -------------------------------------------------

            if reservation:

                messages.success(
                    request,
                    f"'{issue.book_copy.book.title}' "
                    f"returned successfully and is now reserved "
                    f"for {reservation.member.first_name} "
                    f"{reservation.member.last_name}."
                )

            else:

                messages.success(
                    request,
                    f"'{issue.book_copy.book.title}' "
                    f"returned successfully."
                )

            return redirect(
                "issue_list"
            )

        except ValidationError as e:

            messages.error(
                request,
                f"Cannot return book: {e}"
            )

        except IntegrityError:

            messages.error(
                request,
                "Book could not be returned because of a "
                "database constraint."
            )

        except Exception as e:

            messages.error(
                request,
                f"Error while returning book: {e}"
            )

    # -----------------------------------------------------
    # RETURN CONFIRMATION FORM
    # -----------------------------------------------------

    return render(
        request,
        "circulation/return_book.html",
        {
            "issue": issue,
            "today": timezone.localdate(),
        }
    )


# =========================================================
# ASSIGN RETURNED COPY TO RESERVATION
# =========================================================

def assign_returned_copy_to_reservation(book_copy):

    # -----------------------------------------------------
    # FIND OLDEST PENDING RESERVATION
    # -----------------------------------------------------

    reservation = (

        Reservation.objects.filter(

            book=book_copy.book,

            status=Reservation.ReservationStatus.PENDING

        ).select_related(

            "member"

        ).order_by(

            "reservation_date",
            "id"

        ).first()
    )

    # -----------------------------------------------------
    # NO PENDING RESERVATION
    # -----------------------------------------------------

    if not reservation:

        # Make sure copy is available

        book_copy.status = (
            BookCopy.CopyStatus.AVAILABLE
        )

        book_copy.save(
            update_fields=[
                "status",
                "updated_at"
            ]
        )

        return None

    # -----------------------------------------------------
    # ASSIGN COPY TO RESERVATION
    # -----------------------------------------------------

    reservation.book_copy = book_copy

    reservation.status = (
        Reservation.ReservationStatus.READY
    )

    reservation.ready_date = (
        timezone.localdate()
    )

    reservation.save(
        update_fields=[
            "book_copy",
            "status",
            "ready_date",
            "updated_at"
        ]
    )

    # -----------------------------------------------------
    # SET COPY RESERVED
    # -----------------------------------------------------

    book_copy.status = (
        BookCopy.CopyStatus.RESERVED
    )

    book_copy.save(
        update_fields=[
            "status",
            "updated_at"
        ]
    )

    return reservation


# =========================================================
# ISSUE DETAIL
# =========================================================

def issue_detail(request, pk):

    issue = get_object_or_404(

        IssueRecord.objects.select_related(

            "member",
            "member__membership_type",
            "book_copy",
            "book_copy__book"

        ),

        pk=pk
    )

    today = timezone.localdate()

    overdue_days = 0

    fine = Decimal("0.00")

    # -----------------------------------------------------
    # CURRENTLY ISSUED
    # -----------------------------------------------------

    if (
        issue.due_date
        and issue.status == IssueRecord.IssueStatus.ISSUED
    ):

        if today > issue.due_date:

            overdue_days = (
                today - issue.due_date
            ).days

            fine = (
                Decimal(overdue_days)
                * issue.member.membership_type.fine_per_day
            )

    # -----------------------------------------------------
    # RETURNED
    # -----------------------------------------------------

    elif (
        issue.status == IssueRecord.IssueStatus.RETURNED
    ):

        fine = issue.fine_amount

        if issue.due_date and issue.return_date:

            if issue.return_date > issue.due_date:

                overdue_days = (
                    issue.return_date
                    - issue.due_date
                ).days

    context = {

        "issue": issue,

        "overdue_days": overdue_days,

        "fine": fine,

        "today": today,
    }

    return render(
        request,
        "circulation/issue_detail.html",
        context
    )


# =========================================================
# OVERDUE BOOKS
# =========================================================

def overdue_books(request):

    today = timezone.localdate()

    search = request.GET.get(
        "search",
        ""
    ).strip()

    issues = IssueRecord.objects.select_related(

        "member",
        "member__membership_type",
        "book_copy",
        "book_copy__book"

    ).filter(

        status=IssueRecord.IssueStatus.ISSUED,

        due_date__lt=today

    ).order_by(

        "due_date"
    )

    if search:

        issues = issues.filter(

            Q(member__member_code__icontains=search) |

            Q(member__first_name__icontains=search) |

            Q(member__last_name__icontains=search) |

            Q(book_copy__book__title__icontains=search) |

            Q(book_copy__accession_number__icontains=search)
        )

    overdue_data = []

    total_fine = Decimal("0.00")

    for issue in issues:

        overdue_days = (
            today - issue.due_date
        ).days

        fine = (
            Decimal(overdue_days)
            * issue.member.membership_type.fine_per_day
        )

        total_fine += fine

        overdue_data.append(
            {
                "issue": issue,
                "overdue_days": overdue_days,
                "fine": fine,
            }
        )

    context = {

        "overdue_data": overdue_data,

        "search": search,

        "today": today,

        "total_overdue": len(overdue_data),

        "total_fine": total_fine,
    }

    return render(
        request,
        "circulation/overdue_books.html",
        context
    )