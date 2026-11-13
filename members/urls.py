from django.urls import path
from . import views


urlpatterns = [

    # ======================================================
    # MEMBER
    # ======================================================

    path(
        "",
        views.member_list,
        name="member_list"
    ),

    path(
        "add/",
        views.member_add,
        name="member_add"
    ),

    path(
        "edit/<int:pk>/",
        views.member_edit,
        name="member_edit"
    ),

    path(
        "delete/<int:pk>/",
        views.member_delete,
        name="member_delete"
    ),


    # ======================================================
    # MEMBERSHIP TYPE
    # ======================================================

    path(
        "membership-types/",
        views.membership_type_list,
        name="membership_type_list"
    ),

    path(
        "membership-types/add/",
        views.membership_type_add,
        name="membership_type_add"
    ),

    path(
        "membership-types/edit/<int:pk>/",
        views.membership_type_edit,
        name="membership_type_edit"
    ),

    path(
        "membership-types/delete/<int:pk>/",
        views.membership_type_delete,
        name="membership_type_delete"
    ),

]