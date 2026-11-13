from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.db import IntegrityError
from django.contrib import messages

from .models import Library


# ==========================================================
# LIBRARY LIST
# ==========================================================

def library_list(request):

    query = request.GET.get("q", "")

    libraries = Library.objects.all().order_by("name")

    if query:
        libraries = libraries.filter(
            name__icontains=query
        )

    return render(
        request,
        "libraries/library_list.html",
        {
            "libraries": libraries,
            "query": query,
        }
    )


# ==========================================================
# ADD LIBRARY
# ==========================================================

def library_add(request):

    if request.method == "POST":

        name = request.POST.get("name")
        description = request.POST.get("description")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")
        pincode = request.POST.get("pincode")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        status = request.POST.get("status") == "1"

        # The model requires a unique code; generate it when the form does not expose one.
        base_code = (slugify(name or "LIBRARY").replace("-", "").upper()[:20] or "LIBRARY")
        code = base_code
        suffix = 1
        while Library.objects.filter(code=code).exists():
            suffix += 1
            code = f"{base_code[:45]}{suffix}"

        library = Library(
            name=name,
            code=code,
            description=description,
            address=address,
            city=city,
            state=state,
            country=country,
            pincode=pincode,
            phone=phone,
            email=email,
            status=status,
        )

        if request.FILES.get("logo"):
            library.logo = request.FILES["logo"]

        try:
            library.save()
        except IntegrityError:
            messages.error(request, "Could not save library. Check the required fields and unique library code.")
            return render(request, "libraries/library_form.html")
        messages.success(request, "Library added successfully.")
        return redirect("library_list")

    return render(
        request,
        "libraries/library_form.html"
    )


# ==========================================================
# EDIT LIBRARY
# ==========================================================

def library_edit(request, pk):

    library = get_object_or_404(
        Library,
        pk=pk
    )

    if request.method == "POST":

        library.name = request.POST.get("name")

        library.description = request.POST.get(
            "description"
        )

        library.address = request.POST.get(
            "address"
        )

        library.city = request.POST.get(
            "city"
        )

        library.state = request.POST.get(
            "state"
        )

        library.country = request.POST.get(
            "country"
        )

        library.pincode = request.POST.get(
            "pincode"
        )

        library.phone = request.POST.get(
            "phone"
        )

        library.email = request.POST.get(
            "email"
        )

        library.status = (
            request.POST.get("status") == "1"
        )

        if request.FILES.get("logo"):
            library.logo = request.FILES["logo"]

        try:
            library.save()
        except IntegrityError:
            messages.error(request, "Could not update library. Check the required fields.")
            return render(request, "libraries/library_form.html", {"library": library})
        messages.success(request, "Library updated successfully.")
        return redirect("library_list")

    return render(
        request,
        "libraries/library_form.html",
        {
            "library": library
        }
    )


# ==========================================================
# DELETE LIBRARY
# ==========================================================

def library_delete(request, pk):

    library = get_object_or_404(
        Library,
        pk=pk
    )

    if request.method == "POST":
        try:
            library.delete()
            messages.success(request, "Library deleted successfully.")
        except Exception:
            messages.error(request, "This library cannot be deleted because other records may depend on it.")
        return redirect("library_list")

    return render(
        request,
        "libraries/library_confirm_delete.html",
        {
            "library": library
        }
    )