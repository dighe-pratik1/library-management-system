from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from .models import Member, MembershipType


# ==========================================================
# MEMBER LIST
# ==========================================================

def member_list(request):

    query = request.GET.get("q", "")

    members = Member.objects.select_related(
        "membership_type"
    ).all().order_by("first_name")

    if query:

        members = members.filter(
            first_name__icontains=query
        ) | members.filter(
            last_name__icontains=query
        ) | members.filter(
            member_code__icontains=query
        )

    return render(
        request,
        "members/member_list.html",
        {
            "members": members,
            "query": query,
        }
    )


# ==========================================================
# ADD MEMBER
# ==========================================================

# ==========================================================
# ADD MEMBER
# ==========================================================

def member_add(request):

    membership_types = MembershipType.objects.filter(
        status=True
    ).order_by("name")

    if request.method == "POST":

        # --------------------------------------------------
        # GET FORM DATA
        # --------------------------------------------------

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        gender = request.POST.get("gender")
        date_of_birth = request.POST.get("date_of_birth") or None
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")

        membership_type_id = request.POST.get(
            "membership_type"
        )

        department = request.POST.get("department")
        course = request.POST.get("course")
        year = request.POST.get("year")
        roll_number = request.POST.get("roll_number")
        expiry_date = request.POST.get("expiry_date") or None

        status = request.POST.get("status") == "1"

        # --------------------------------------------------
        # AUTOMATIC MEMBER CODE
        # --------------------------------------------------

        last_member = Member.objects.order_by("-id").first()

        if last_member:
            try:
                last_number = int(
                    last_member.member_code.replace("SCL", "")
                )
                next_number = last_number + 1
            except (ValueError, AttributeError):
                next_number = 1
        else:
            next_number = 1

        member_code = f"SCL{next_number:03d}"

        # --------------------------------------------------
        # CREATE MEMBER
        # --------------------------------------------------

        member = Member(
            member_code=member_code,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            date_of_birth=date_of_birth,
            mobile=mobile,
            email=email,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            membership_type_id=membership_type_id,
            department=department,
            course=course,
            year=year,
            roll_number=roll_number,
            expiry_date=expiry_date,
            status=status,
        )

        if request.FILES.get("photo"):
            member.photo = request.FILES["photo"]

        try:
            member.save()
        except IntegrityError:
            # If same member code already exists,
            # generate next code and try again.
            last_member = Member.objects.order_by("-id").first()

            if last_member:
                try:
                    last_number = int(
                        last_member.member_code.replace("SCL", "")
                    )
                    next_number = last_number + 1
                except (ValueError, AttributeError):
                    next_number = 1
            else:
                next_number = 1

            member.member_code = f"SCL{next_number:03d}"
            member.save()

        return redirect("member_list")

    return render(
        request,
        "members/member_form.html",
        {
            "membership_types": membership_types,
        }
    )

# ==========================================================
# EDIT MEMBER
# ==========================================================

def member_edit(request, pk):

    member = get_object_or_404(
        Member,
        pk=pk
    )

    membership_types = MembershipType.objects.filter(
        status=True
    ).order_by("name")

    if request.method == "POST":

        member.member_code = request.POST.get(
            "member_code"
        )

        member.first_name = request.POST.get(
            "first_name"
        )

        member.last_name = request.POST.get(
            "last_name"
        )

        member.gender = request.POST.get(
            "gender"
        )

        member.date_of_birth = (
            request.POST.get("date_of_birth")
            or None
        )

        member.mobile = request.POST.get(
            "mobile"
        )

        member.email = request.POST.get(
            "email"
        )

        member.address = request.POST.get(
            "address"
        )

        member.city = request.POST.get(
            "city"
        )

        member.state = request.POST.get(
            "state"
        )

        member.pincode = request.POST.get(
            "pincode"
        )

        member.membership_type_id = request.POST.get(
            "membership_type"
        )

        member.department = request.POST.get(
            "department"
        )

        member.course = request.POST.get(
            "course"
        )

        member.year = request.POST.get(
            "year"
        )

        member.roll_number = request.POST.get(
            "roll_number"
        )

        member.expiry_date = (
            request.POST.get("expiry_date")
            or None
        )

        member.status = (
            request.POST.get("status") == "1"
        )

        if request.FILES.get("photo"):
            member.photo = request.FILES["photo"]

        member.save()

        return redirect("member_list")

    return render(
        request,
        "members/member_form.html",
        {
            "member": member,
            "membership_types": membership_types,
        }
    )


# ==========================================================
# DELETE MEMBER
# ==========================================================

def member_delete(request, pk):

    member = get_object_or_404(
        Member,
        pk=pk
    )

    if request.method == "POST":

        member.delete()

        return redirect("member_list")

    return render(
        request,
        "members/member_confirm_delete.html",
        {
            "member": member
        }
    )
# ==========================================================
# MEMBERSHIP TYPE LIST
# ==========================================================

def membership_type_list(request):

    query = request.GET.get("q", "")

    membership_types = MembershipType.objects.all().order_by("name")

    if query:
        membership_types = membership_types.filter(
            name__icontains=query
        )

    return render(
        request,
        "members/membership_type_list.html",
        {
            "membership_types": membership_types,
            "query": query,
        }
    )


# ==========================================================
# ADD MEMBERSHIP TYPE
# ==========================================================

def membership_type_add(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        max_books = request.POST.get("max_books", 3)
        loan_days = request.POST.get("loan_days", 14)
        renewal_limit = request.POST.get("renewal_limit", 2)

        fine_per_day = request.POST.get("fine_per_day", 2)
        membership_fee = request.POST.get("membership_fee", 0)

        status = request.POST.get("status") == "1"

        if not name:
            return render(
                request,
                "members/membership_type_form.html",
                {
                    "error": "Membership Type name is required."
                }
            )

        if MembershipType.objects.filter(name=name).exists():
            return render(
                request,
                "members/membership_type_form.html",
                {
                    "error": "Membership Type already exists."
                }
            )

        MembershipType.objects.create(
            name=name,
            description=description,
            max_books=max_books,
            loan_days=loan_days,
            renewal_limit=renewal_limit,
            fine_per_day=fine_per_day,
            membership_fee=membership_fee,
            status=status,
        )

        return redirect("membership_type_list")

    return render(
        request,
        "members/membership_type_form.html"
    )


# ==========================================================
# EDIT MEMBERSHIP TYPE
# ==========================================================

def membership_type_edit(request, pk):

    membership_type = get_object_or_404(
        MembershipType,
        pk=pk
    )

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        max_books = request.POST.get("max_books", 3)
        loan_days = request.POST.get("loan_days", 14)
        renewal_limit = request.POST.get("renewal_limit", 2)

        fine_per_day = request.POST.get("fine_per_day", 2)
        membership_fee = request.POST.get("membership_fee", 0)

        status = request.POST.get("status") == "1"

        if not name:
            return render(
                request,
                "members/membership_type_form.html",
                {
                    "membership_type": membership_type,
                    "error": "Membership Type name is required."
                }
            )

        if MembershipType.objects.filter(
            name=name
        ).exclude(
            pk=pk
        ).exists():

            return render(
                request,
                "members/membership_type_form.html",
                {
                    "membership_type": membership_type,
                    "error": "Membership Type already exists."
                }
            )

        membership_type.name = name
        membership_type.description = description
        membership_type.max_books = max_books
        membership_type.loan_days = loan_days
        membership_type.renewal_limit = renewal_limit
        membership_type.fine_per_day = fine_per_day
        membership_type.membership_fee = membership_fee
        membership_type.status = status

        membership_type.save()

        return redirect("membership_type_list")

    return render(
        request,
        "members/membership_type_form.html",
        {
            "membership_type": membership_type
        }
    )


# ==========================================================
# DELETE MEMBERSHIP TYPE
# ==========================================================

def membership_type_delete(request, pk):

    membership_type = get_object_or_404(
        MembershipType,
        pk=pk
    )

    if request.method == "POST":
        try:
            membership_type.delete()
            messages.success(request, "Membership type deleted successfully.")
        except Exception:
            messages.error(request, "This membership type is assigned to members and cannot be deleted.")
        return redirect("membership_type_list")

    return render(
        request,
        "members/membership_type_confirm_delete.html",
        {
            "membership_type": membership_type
        }
    )