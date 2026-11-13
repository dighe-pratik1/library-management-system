from django.urls import path

from . import views


urlpatterns = [

    # Reservation list
    path(
        "",
        views.reservation_list,
        name="reservation_list"
    ),

    # Add reservation
    path(
        "add/",
        views.reservation_add,
        name="reservation_add"
    ),

    # Detail
    path(
        "detail/<int:pk>/",
        views.reservation_detail,
        name="reservation_detail"
    ),

    # Fulfill
    path(
        "fulfill/<int:pk>/",
        views.reservation_fulfill,
        name="reservation_fulfill"
    ),

    # Cancel
    path(
        "cancel/<int:pk>/",
        views.reservation_cancel,
        name="reservation_cancel"
    ),

    # Delete
    path(
        "delete/<int:pk>/",
        views.reservation_delete,
        name="reservation_delete"
    ),

]