from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.notification_list,
        name="notification_list"
    ),

    path(
        "add/",
        views.notification_add,
        name="notification_add"
    ),

    path(
        "<int:pk>/",
        views.notification_detail,
        name="notification_detail"
    ),

    path(
        "<int:pk>/read/",
        views.notification_read,
        name="notification_read"
    ),

    path(
        "<int:pk>/unread/",
        views.notification_unread,
        name="notification_unread"
    ),

    path(
        "read-all/",
        views.notification_read_all,
        name="notification_read_all"
    ),

    path(
        "<int:pk>/delete/",
        views.notification_delete,
        name="notification_delete"
    ),
]