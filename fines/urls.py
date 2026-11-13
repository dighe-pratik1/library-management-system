from django.urls import path

from . import views


urlpatterns = [

    # Fine list
    path(
        "",
        views.fine_list,
        name="fine_list"
    ),

    # Add fine
    path(
        "add/",
        views.fine_add,
        name="fine_add"
    ),

    # Fine detail
    path(
        "<int:pk>/",
        views.fine_detail,
        name="fine_detail"
    ),

    # Edit
    path(
        "<int:pk>/edit/",
        views.fine_edit,
        name="fine_edit"
    ),

    # Pay
    path(
        "<int:pk>/pay/",
        views.fine_pay,
        name="fine_pay"
    ),

    # Delete
    path(
        "<int:pk>/delete/",
        views.fine_delete,
        name="fine_delete"
    ),
]