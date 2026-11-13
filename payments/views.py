from decimal import Decimal

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages

from django.utils import timezone

from django.db.models import Q, Sum

from .models import Payment

from fines.models import Fine


# =========================================================
# PAYMENT LIST
# =========================================================
def payment_list(request):

    payments = Payment.objects.select_related(
        "fine",
        "member",
        "fine__issue_record",
        "fine__issue_record__book_copy",
        "fine__issue_record__book_copy__book"
    ).all().order_by(
        "-payment_date",
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

        payments = payments.filter(

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
                transaction_id__icontains=search
            )
            |
            Q(
                fine__issue_record__book_copy__book__title__icontains=search
            )
        )

    # -----------------------------------------------------
    # Payment method filter
    # -----------------------------------------------------

    method = request.GET.get(
        "method",
        ""
    ).strip()

    if method:

        payments = payments.filter(
            payment_method=method
        )

    # -----------------------------------------------------
    # Status filter
    # -----------------------------------------------------

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if status:

        payments = payments.filter(
            status=status
        )

    # -----------------------------------------------------
    # Totals
    # -----------------------------------------------------

    total_paid = sum(
        (
            payment.amount
            for payment in payments
            if payment.status == Payment.PaymentStatus.SUCCESS
        ),
        Decimal("0.00")
    )

    total_transactions = payments.count()

    # -----------------------------------------------------
    # Context
    # -----------------------------------------------------

    context = {

        "payments": payments,

        "total_paid": total_paid,

        "total_transactions": total_transactions,

        "search": search,

        "method": method,

        "status": status,

        "payment_methods": Payment.PaymentMethod.choices,

        "payment_statuses": Payment.PaymentStatus.choices,
    }

    return render(
        request,
        "payments/payment_list.html",
        context
    )


# =========================================================
# ADD PAYMENT
# =========================================================
def payment_add(request):

    if request.method == "POST":

        fine_id = request.POST.get(
            "fine"
        )

        amount_text = request.POST.get(
            "amount",
            ""
        ).strip()

        payment_method = request.POST.get(
            "payment_method",
            Payment.PaymentMethod.CASH
        )

        transaction_id = request.POST.get(
            "transaction_id",
            ""
        ).strip()

        notes = request.POST.get(
            "notes",
            ""
        ).strip()

        # -------------------------------------------------
        # Validate fine
        # -------------------------------------------------

        if not fine_id:

            messages.error(
                request,
                "Please select a fine."
            )

            return redirect(
                "payment_add"
            )

        fine = get_object_or_404(
            Fine,
            pk=fine_id
        )

        # -------------------------------------------------
        # Amount
        # -------------------------------------------------

        try:

            amount = Decimal(
                amount_text
            )

        except Exception:

            messages.error(
                request,
                "Please enter a valid payment amount."
            )

            return redirect(
                "payment_add"
            )

        # -------------------------------------------------
        # Positive amount
        # -------------------------------------------------

        if amount <= Decimal("0.00"):

            messages.error(
                request,
                "Payment amount must be greater than zero."
            )

            return redirect(
                "payment_add"
            )

        # -------------------------------------------------
        # Remaining fine balance
        # -------------------------------------------------

        remaining = (
            fine.amount -
            fine.paid_amount
        )

        if remaining <= Decimal("0.00"):

            messages.error(
                request,
                "This fine is already fully paid."
            )

            return redirect(
                "payment_add"
            )

        # -------------------------------------------------
        # Payment cannot exceed balance
        # -------------------------------------------------

        if amount > remaining:

            messages.error(
                request,
                "Payment cannot be greater than remaining balance."
            )

            return redirect(
                "payment_add"
            )

        # -------------------------------------------------
        # Valid payment method
        # -------------------------------------------------

        valid_methods = [
            choice[0]
            for choice in Payment.PaymentMethod.choices
        ]

        if payment_method not in valid_methods:

            payment_method = Payment.PaymentMethod.CASH

        # -------------------------------------------------
        # Create Payment
        # -------------------------------------------------

        payment = Payment.objects.create(

            fine=fine,

            member=fine.member,

            amount=amount,

            payment_method=payment_method,

            transaction_id=transaction_id,

            status=Payment.PaymentStatus.SUCCESS,

            payment_date=timezone.localdate(),

            notes=notes,
        )

        # -------------------------------------------------
        # Update Fine
        # -------------------------------------------------

        fine.paid_amount = (
            fine.paid_amount +
            amount
        )

        fine.save()

        messages.success(
            request,
            "Payment recorded successfully."
        )

        return redirect(
            "payment_detail",
            pk=payment.pk
        )

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    fines = Fine.objects.select_related(
        "member",
        "issue_record",
        "issue_record__book_copy",
        "issue_record__book_copy__book"
    ).filter(
        balance__gt=0
    ).order_by(
        "-fine_date",
        "-id"
    )

    context = {

        "fines": fines,

        "payment_methods": Payment.PaymentMethod.choices,
    }

    return render(
        request,
        "payments/payment_form.html",
        context
    )


# =========================================================
# PAYMENT DETAIL
# =========================================================
def payment_detail(request, pk):

    payment = get_object_or_404(

        Payment.objects.select_related(
            "fine",
            "member",
            "fine__issue_record",
            "fine__issue_record__book_copy",
            "fine__issue_record__book_copy__book"
        ),

        pk=pk
    )

    return render(
        request,
        "payments/payment_detail.html",
        {
            "payment": payment
        }
    )


# =========================================================
# EDIT PAYMENT
# =========================================================
def payment_edit(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk
    )

    if request.method == "POST":

        payment_method = request.POST.get(
            "payment_method",
            Payment.PaymentMethod.CASH
        )

        transaction_id = request.POST.get(
            "transaction_id",
            ""
        ).strip()

        notes = request.POST.get(
            "notes",
            ""
        ).strip()

        # -------------------------------------------------
        # Update only payment information
        # -------------------------------------------------

        valid_methods = [
            choice[0]
            for choice in Payment.PaymentMethod.choices
        ]

        if payment_method not in valid_methods:

            payment_method = Payment.PaymentMethod.CASH

        payment.payment_method = payment_method

        payment.transaction_id = transaction_id

        payment.notes = notes

        payment.save()

        messages.success(
            request,
            "Payment updated successfully."
        )

        return redirect(
            "payment_detail",
            pk=pk
        )

    return render(
        request,
        "payments/payment_edit.html",
        {
            "payment": payment,

            "payment_methods": Payment.PaymentMethod.choices,
        }
    )


# =========================================================
# DELETE PAYMENT
# =========================================================
def payment_delete(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk
    )

    if request.method == "POST":

        # -------------------------------------------------
        # Store amount before deleting
        # -------------------------------------------------

        amount = payment.amount

        fine = payment.fine

        # -------------------------------------------------
        # Delete payment
        # -------------------------------------------------

        payment.delete()

        # -------------------------------------------------
        # Recalculate fine paid amount
        # -------------------------------------------------

        successful_payments = Payment.objects.filter(
            fine=fine,
            status=Payment.PaymentStatus.SUCCESS
        ).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        fine.paid_amount = successful_payments

        fine.save()

        messages.success(
            request,
            "Payment deleted successfully."
        )

        return redirect(
            "payment_list"
        )

    return render(
        request,
        "payments/payment_detail.html",
        {
            "payment": payment,
            "delete_confirm": True
        }
    )