from decimal import Decimal

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages

from django.utils import timezone

from django.db.models import Q

from .models import Fine

from members.models import IssueRecord


# =========================================================
# FINE LIST
# =========================================================
def fine_list(request):

    # -----------------------------------------------------
    # Automatically create Fine records from existing
    # IssueRecord records where fine_amount > 0
    # -----------------------------------------------------

    issue_records = IssueRecord.objects.filter(
        fine_amount__gt=0
    ).select_related(
        "member",
        "book_copy",
        "book_copy__book"
    )

    for issue in issue_records:

        Fine.objects.get_or_create(

            issue_record=issue,

            defaults={
                "member": issue.member,

                "amount": Decimal(
                    str(issue.fine_amount or 0)
                ),

                "paid_amount": Decimal(
                    "0.00"
                ),

                "reason": "Late return",

                "fine_date": (
                    issue.return_date
                    or timezone.localdate()
                ),
            }
        )

    # -----------------------------------------------------
    # Get all fines
    # -----------------------------------------------------

    fines = Fine.objects.select_related(
        "member",
        "issue_record",
        "issue_record__book_copy",
        "issue_record__book_copy__book"
    ).all().order_by(
        "-fine_date",
        "-id"
    )

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        fines = fines.filter(
            Q(
                member__first_name__icontains=search
            )
            |
            Q(
                member__last_name__icontains=search
            )
            |
            Q(
                member__member_code__icontains=search
            )
            |
            Q(
                issue_record__book_copy__book__title__icontains=search
            )
        )

    # -----------------------------------------------------
    # Status filter
    # -----------------------------------------------------

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if status:

        fines = fines.filter(
            status=status
        )

    # -----------------------------------------------------
    # Totals
    # -----------------------------------------------------

    total_amount = sum(
        (
            fine.amount
            for fine in fines
        ),
        Decimal("0.00")
    )

    total_paid = sum(
        (
            fine.paid_amount
            for fine in fines
        ),
        Decimal("0.00")
    )

    total_balance = sum(
        (
            fine.balance
            for fine in fines
        ),
        Decimal("0.00")
    )

    # -----------------------------------------------------
    # Context
    # -----------------------------------------------------

    context = {

        "fines": fines,

        "total_amount": total_amount,

        "total_paid": total_paid,

        "total_balance": total_balance,

        "search": search,

        "status": status,
    }

    return render(
        request,
        "fines/fine_list.html",
        context
    )


# =========================================================
# ADD FINE
# =========================================================
def fine_add(request):

    if request.method == "POST":

        issue_id = request.POST.get(
            "issue_record"
        )

        amount_text = request.POST.get(
            "amount",
            "0"
        )

        reason = request.POST.get(
            "reason",
            ""
        ).strip()

        notes = request.POST.get(
            "notes",
            ""
        ).strip()

        # -------------------------------------------------
        # Validate issue
        # -------------------------------------------------

        if not issue_id:

            messages.error(
                request,
                "Please select an issue record."
            )

            return redirect(
                "fine_add"
            )

        issue = get_object_or_404(
            IssueRecord,
            pk=issue_id
        )

        # -------------------------------------------------
        # Convert amount
        # -------------------------------------------------

        try:

            amount = Decimal(
                amount_text
            )

        except Exception:

            messages.error(
                request,
                "Please enter a valid fine amount."
            )

            return redirect(
                "fine_add"
            )

        # -------------------------------------------------
        # Validate amount
        # -------------------------------------------------

        if amount < Decimal("0.00"):

            messages.error(
                request,
                "Fine amount cannot be negative."
            )

            return redirect(
                "fine_add"
            )

        # -------------------------------------------------
        # Create or update
        # -------------------------------------------------

        fine, created = Fine.objects.update_or_create(

            issue_record=issue,

            defaults={
                "member": issue.member,

                "amount": amount,

                "reason": (
                    reason
                    or "Late return"
                ),

                "notes": notes,

                "fine_date": (
                    issue.return_date
                    or timezone.localdate()
                ),
            }
        )

        messages.success(
            request,
            "Fine added successfully."
        )

        return redirect(
            "fine_list"
        )

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    issues = IssueRecord.objects.select_related(
        "member",
        "book_copy",
        "book_copy__book"
    ).all().order_by(
        "-id"
    )

    return render(
        request,
        "fines/fine_form.html",
        {
            "issues": issues
        }
    )


# =========================================================
# FINE DETAIL
# =========================================================
def fine_detail(request, pk):

    fine = get_object_or_404(

        Fine.objects.select_related(
            "member",
            "issue_record",
            "issue_record__book_copy",
            "issue_record__book_copy__book"
        ),

        pk=pk
    )

    return render(
        request,
        "fines/fine_detail.html",
        {
            "fine": fine
        }
    )


# =========================================================
# EDIT FINE
# =========================================================
def fine_edit(request, pk):

    fine = get_object_or_404(
        Fine,
        pk=pk
    )

    if request.method == "POST":

        amount_text = request.POST.get(
            "amount",
            "0"
        )

        reason = request.POST.get(
            "reason",
            ""
        ).strip()

        notes = request.POST.get(
            "notes",
            ""
        ).strip()

        # -------------------------------------------------
        # Convert amount
        # -------------------------------------------------

        try:

            amount = Decimal(
                amount_text
            )

        except Exception:

            messages.error(
                request,
                "Please enter a valid fine amount."
            )

            return redirect(
                "fine_edit",
                pk=pk
            )

        # -------------------------------------------------
        # Validate
        # -------------------------------------------------

        if amount < Decimal("0.00"):

            messages.error(
                request,
                "Fine amount cannot be negative."
            )

            return redirect(
                "fine_edit",
                pk=pk
            )

        # -------------------------------------------------
        # Don't allow editing below already paid amount
        # -------------------------------------------------

        if amount < fine.paid_amount:

            messages.error(
                request,
                "Fine amount cannot be less than the amount already paid."
            )

            return redirect(
                "fine_edit",
                pk=pk
            )

        # -------------------------------------------------
        # Update
        # -------------------------------------------------

        fine.amount = amount

        fine.reason = (
            reason
            or "Late return"
        )

        fine.notes = notes

        fine.save()

        messages.success(
            request,
            "Fine updated successfully."
        )

        return redirect(
            "fine_detail",
            pk=pk
        )

    return render(
        request,
        "fines/fine_edit.html",
        {
            "fine": fine
        }
    )


# =========================================================
# PAY FINE
# =========================================================
def fine_pay(request, pk):

    fine = get_object_or_404(
        Fine,
        pk=pk
    )

    # -----------------------------------------------------
    # Current balance
    # -----------------------------------------------------

    remaining = (
        fine.amount
        - fine.paid_amount
    )

    if remaining < Decimal("0.00"):

        remaining = Decimal(
            "0.00"
        )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        paid_amount_text = request.POST.get(
            "paid_amount",
            ""
        ).strip()

        # -------------------------------------------------
        # Empty payment
        # -------------------------------------------------

        if not paid_amount_text:

            messages.error(
                request,
                "Please enter payment amount."
            )

            return redirect(
                "fine_pay",
                pk=pk
            )

        # -------------------------------------------------
        # Convert payment
        # -------------------------------------------------

        try:

            paid_amount = Decimal(
                paid_amount_text
            )

        except Exception:

            messages.error(
                request,
                "Please enter a valid payment amount."
            )

            return redirect(
                "fine_pay",
                pk=pk
            )

        # -------------------------------------------------
        # Validate positive
        # -------------------------------------------------

        if paid_amount <= Decimal("0.00"):

            messages.error(
                request,
                "Payment amount must be greater than 0."
            )

            return redirect(
                "fine_pay",
                pk=pk
            )

        # -------------------------------------------------
        # Check already paid
        # -------------------------------------------------

        if remaining <= Decimal("0.00"):

            messages.error(
                request,
                "This fine is already fully paid."
            )

            return redirect(
                "fine_detail",
                pk=pk
            )

        # -------------------------------------------------
        # Payment greater than balance
        # -------------------------------------------------

        if paid_amount > remaining:

            messages.error(
                request,
                "Payment cannot be greater than remaining balance."
            )

            return redirect(
                "fine_pay",
                pk=pk
            )

        # -------------------------------------------------
        # Add payment
        # -------------------------------------------------

        fine.paid_amount = (
            fine.paid_amount
            + paid_amount
        )

        # -------------------------------------------------
        # SAVE
        #
        # Fine.save() automatically calculates:
        # balance
        # status
        # paid_date
        # -------------------------------------------------

        fine.save()

        messages.success(
            request,
            "Payment recorded successfully."
        )

        return redirect(
            "fine_detail",
            pk=pk
        )

    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "fines/fine_payment.html",
        {
            "fine": fine,
            "remaining": remaining,
        }
    )


# =========================================================
# DELETE FINE
# =========================================================
def fine_delete(request, pk):

    fine = get_object_or_404(
        Fine,
        pk=pk
    )

    # -----------------------------------------------------
    # Delete only through POST
    # -----------------------------------------------------

    if request.method == "POST":

        fine.delete()

        messages.success(
            request,
            "Fine deleted successfully."
        )

        return redirect(
            "fine_list"
        )

    return render(
        request,
        "fines/fine_detail.html",
        {
            "fine": fine,
            "delete_confirm": True
        }
    )


# =========================================================
# GENERATE FINE FROM ISSUE
# =========================================================
def generate_fine_from_issue(issue):

    if not issue:
        return None

    # -----------------------------------------------------
    # Calculate fine in IssueRecord
    # -----------------------------------------------------

    issue.calculate_fine()

    amount = Decimal(
        str(
            issue.fine_amount
            or 0
        )
    )

    # -----------------------------------------------------
    # No fine
    # -----------------------------------------------------

    if amount <= Decimal("0.00"):

        return None

    # -----------------------------------------------------
    # Create or update Fine
    # -----------------------------------------------------

    fine, created = Fine.objects.update_or_create(

        issue_record=issue,

        defaults={
            "member": issue.member,

            "amount": amount,

            "reason": "Late return",

            "fine_date": (
                issue.return_date
                or timezone.localdate()
            ),
        }
    )

    return fine