from datetime import datetime
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)
from django.utils import timezone

from .models import Reservation

from members.models import Member, IssueRecord
from books.models import Book, BookCopy


# ==========================================================
# RESERVATION LIST
# ==========================================================

def reservation_list(request):

    search = request.GET.get(
        "q",
        ""
    ).strip()

    reservations = Reservation.objects.select_related(
        "member",
        "book",
        "book_copy"
    ).all()

    if search:

        reservations = reservations.filter(
            Q(member__member_code__icontains=search) |
            Q(member__first_name__icontains=search) |
            Q(member__last_name__icontains=search) |
            Q(book__title__icontains=search) |
            Q(book__isbn__icontains=search) |
            Q(book_copy__accession_number__icontains=search)
        )

    total_reservations = reservations.count()

    pending_count = reservations.filter(
        status=Reservation.ReservationStatus.PENDING
    ).count()

    ready_count = reservations.filter(
        status=Reservation.ReservationStatus.READY
    ).count()

    fulfilled_count = reservations.filter(
        status=Reservation.ReservationStatus.FULFILLED
    ).count()

    cancelled_count = reservations.filter(
        status=Reservation.ReservationStatus.CANCELLED
    ).count()

    context = {

        "reservations": reservations,

        "search": search,

        "total_reservations": total_reservations,

        "pending_count": pending_count,

        "ready_count": ready_count,

        "fulfilled_count": fulfilled_count,

        "cancelled_count": cancelled_count,
    }

    return render(
        request,
        "reservations/reservation_list.html",
        context
    )


# ==========================================================
# ADD RESERVATION
# ==========================================================

def reservation_add(request):

    members = Member.objects.filter(
        status=True
    ).select_related(
        "membership_type"
    ).order_by(
        "first_name",
        "last_name"
    )

    books = Book.objects.filter(
        status=True
    ).select_related(
        "author",
        "publisher",
        "category"
    ).order_by(
        "title"
    )

    if request.method == "POST":

        member_id = request.POST.get(
            "member"
        )

        book_id = request.POST.get(
            "book"
        )

        reservation_date_text = request.POST.get(
            "reservation_date"
        )

        notes = request.POST.get(
            "notes",
            ""
        ).strip()

        # --------------------------------------------------
        # VALIDATE MEMBER
        # --------------------------------------------------

        if not member_id:

            messages.error(
                request,
                "Please select a member."
            )

            return redirect(
                "reservation_add"
            )

        # --------------------------------------------------
        # VALIDATE BOOK
        # --------------------------------------------------

        if not book_id:

            messages.error(
                request,
                "Please select a book."
            )

            return redirect(
                "reservation_add"
            )

        member = get_object_or_404(
            Member,
            pk=member_id,
            status=True
        )

        book = get_object_or_404(
            Book,
            pk=book_id,
            status=True
        )

        # --------------------------------------------------
        # RESERVATION DATE
        # --------------------------------------------------

        if reservation_date_text:

            try:

                reservation_date = datetime.strptime(
                    reservation_date_text,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                messages.error(
                    request,
                    "Invalid reservation date."
                )

                return redirect(
                    "reservation_add"
                )

        else:

            reservation_date = timezone.localdate()

        # --------------------------------------------------
        # CHECK EXISTING ACTIVE RESERVATION
        # --------------------------------------------------

        already_reserved = Reservation.objects.filter(
            member=member,
            book=book,
            status__in=[
                Reservation.ReservationStatus.PENDING,
                Reservation.ReservationStatus.READY
            ]
        ).exists()

        if already_reserved:

            messages.warning(
                request,
                "This member already has an active reservation for this book."
            )

            return redirect(
                "reservation_list"
            )

        # --------------------------------------------------
        # FIND AVAILABLE COPY
        # --------------------------------------------------

        available_copy = BookCopy.objects.filter(
            book=book,
            status=BookCopy.CopyStatus.AVAILABLE
        ).order_by(
            "accession_number"
        ).first()

        # --------------------------------------------------
        # CREATE RESERVATION
        # --------------------------------------------------

        try:

            with transaction.atomic():

                if available_copy:

                    reservation = Reservation.objects.create(

                        member=member,

                        book=book,

                        book_copy=available_copy,

                        reservation_date=reservation_date,

                        ready_date=reservation_date,

                        status=Reservation.ReservationStatus.READY,

                        notes=notes
                    )

                    # Reserve the physical copy
                    available_copy.status = (
                        BookCopy.CopyStatus.RESERVED
                    )

                    available_copy.save(
                        update_fields=[
                            "status",
                            "updated_at"
                        ]
                    )

                    messages.success(
                        request,
                        f"'{book.title}' reserved successfully. "
                        f"Copy {available_copy.accession_number} is READY."
                    )

                else:

                    Reservation.objects.create(

                        member=member,

                        book=book,

                        reservation_date=reservation_date,

                        status=Reservation.ReservationStatus.PENDING,

                        notes=notes
                    )

                    messages.success(
                        request,
                        f"'{book.title}' reservation created. "
                        f"It is currently PENDING."
                    )

            return redirect(
                "reservation_list"
            )

        except ValidationError as e:

            messages.error(
                request,
                f"Cannot create reservation: {e}"
            )

            return redirect(
                "reservation_add"
            )


    context = {

        "members": members,

        "books": books,

        "today": timezone.localdate(),
    }

    return render(
        request,
        "reservations/reservation_form.html",
        context
    )


# ==========================================================
# RESERVATION DETAIL
# ==========================================================

def reservation_detail(request, pk):

    reservation = get_object_or_404(
        Reservation.objects.select_related(
            "member",
            "member__membership_type",
            "book",
            "book__author",
            "book__publisher",
            "book_copy"
        ),
        pk=pk
    )

    return render(
        request,
        "reservations/reservation_detail.html",
        {
            "reservation": reservation
        }
    )


# ==========================================================
# FULFILL RESERVATION
# ==========================================================

def reservation_fulfill(request, pk):

    reservation = get_object_or_404(
        Reservation.objects.select_related(
            "member",
            "book",
            "book_copy"
        ),
        pk=pk
    )

    if reservation.status != Reservation.ReservationStatus.READY:

        messages.error(
            request,
            "Only READY reservations can be fulfilled."
        )

        return redirect(
            "reservation_list"
        )

    if not reservation.book_copy:

        messages.error(
            request,
            "No book copy is assigned to this reservation."
        )

        return redirect(
            "reservation_list"
        )

    if reservation.book_copy.status != BookCopy.CopyStatus.RESERVED:

        messages.error(
            request,
            "The reserved book copy is not available."
        )

        return redirect(
            "reservation_list"
        )

    # ------------------------------------------------------
    # CHECK MEMBER BOOK LIMIT
    # ------------------------------------------------------

    current_books = IssueRecord.objects.filter(
        member=reservation.member,
        status=IssueRecord.IssueStatus.ISSUED
    ).count()

    max_books = (
        reservation.member.membership_type.max_books
    )

    if current_books >= max_books:

        messages.error(
            request,
            f"{reservation.member.first_name} has reached "
            f"the maximum limit of {max_books} books."
        )

        return redirect(
            "reservation_list"
        )

    try:

        with transaction.atomic():

            # Create issue record
            issue = IssueRecord(

                member=reservation.member,

                book_copy=reservation.book_copy,

                issue_date=timezone.localdate(),

                status=IssueRecord.IssueStatus.ISSUED,

                notes=(
                    f"Issued from reservation #{reservation.id}"
                )
            )

            issue.save()

            # Update reservation
            reservation.status = (
                Reservation.ReservationStatus.FULFILLED
            )

            reservation.fulfilled_date = (
                timezone.localdate()
            )

            reservation.save(
                update_fields=[
                    "status",
                    "fulfilled_date",
                    "updated_at"
                ]
            )

        messages.success(
            request,
            f"'{reservation.book.title}' issued successfully "
            f"to {reservation.member.first_name} "
            f"{reservation.member.last_name}."
        )

    except ValidationError as e:

        messages.error(
            request,
            f"Cannot fulfill reservation: {e}"
        )

    except Exception as e:

        messages.error(
            request,
            f"Error while fulfilling reservation: {e}"
        )

    return redirect(
        "reservation_list"
    )


# ==========================================================
# CANCEL RESERVATION
# ==========================================================

def reservation_cancel(request, pk):

    reservation = get_object_or_404(
        Reservation.objects.select_related(
            "book",
            "book_copy"
        ),
        pk=pk
    )

    if request.method == "POST":

        try:

            with transaction.atomic():

                # Release reserved copy
                if (
                    reservation.book_copy
                    and reservation.status
                    == Reservation.ReservationStatus.READY
                ):

                    if (
                        reservation.book_copy.status
                        == BookCopy.CopyStatus.RESERVED
                    ):

                        reservation.book_copy.status = (
                            BookCopy.CopyStatus.AVAILABLE
                        )

                        reservation.book_copy.save(
                            update_fields=[
                                "status",
                                "updated_at"
                            ]
                        )

                reservation.status = (
                    Reservation.ReservationStatus.CANCELLED
                )

                reservation.cancelled_date = (
                    timezone.localdate()
                )

                reservation.save(
                    update_fields=[
                        "status",
                        "cancelled_date",
                        "updated_at"
                    ]
                )

            messages.success(
                request,
                "Reservation cancelled successfully."
            )

        except Exception as e:

            messages.error(
                request,
                f"Error cancelling reservation: {e}"
            )

        return redirect(
            "reservation_list"
        )

    return render(
        request,
        "reservations/reservation_cancel.html",
        {
            "reservation": reservation
        }
    )


# ==========================================================
# DELETE RESERVATION
# ==========================================================

def reservation_delete(request, pk):

    reservation = get_object_or_404(
        Reservation,
        pk=pk
    )

    if request.method == "POST":

        # Do not delete active READY reservation
        if reservation.status == (
            Reservation.ReservationStatus.READY
        ):

            if reservation.book_copy:

                if (
                    reservation.book_copy.status
                    == BookCopy.CopyStatus.RESERVED
                ):

                    reservation.book_copy.status = (
                        BookCopy.CopyStatus.AVAILABLE
                    )

                    reservation.book_copy.save(
                        update_fields=[
                            "status",
                            "updated_at"
                        ]
                    )

        reservation.delete()

        messages.success(
            request,
            "Reservation deleted successfully."
        )

        return redirect(
            "reservation_list"
        )

    return render(
        request,
        "reservations/reservation_cancel.html",
        {
            "reservation": reservation,
            "delete_mode": True
        }
    )