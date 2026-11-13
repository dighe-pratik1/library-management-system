from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "",
        include("dashboard.urls")
    ),

    path(
        "books/",
        include("books.urls")
    ),

    path(
        "members/",
        include("members.urls")
    ),

    path(
        "libraries/",
        include("libraries.urls")
    ),

    path(
        "circulation/",
        include("circulation.urls")
    ),

    path(
        "fines/",
        include("fines.urls")
    ),

    path(
        "reservations/",
        include("reservations.urls")
    ),

    path(
        "notifications/",
        include("notifications.urls")
    ),

    path(
        "payments/",
        include("payments.urls")
    ),
    path("accounts/", include("accounts.urls")),
    path(
        "reports/",
        include("reports.urls")
    ),
]