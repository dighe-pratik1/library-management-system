from django.urls import path
from . import views


urlpatterns = [

    # Circulation dashboard
    path(
        "",
        views.circulation_home,
        name="circulation_home"
    ),

    # Issue list
    path(
        "issues/",
        views.issue_list,
        name="issue_list"
    ),

    # Issue book
    path(
        "issue/",
        views.issue_book,
        name="issue_book"
    ),

    # Return book
    path(
        "return/<int:pk>/",
        views.return_book,
        name="return_book"
    ),

    # Issue detail
    path(
        "detail/<int:pk>/",
        views.issue_detail,
        name="issue_detail"
    ),

    # Overdue books
    path(
        "overdue/",
        views.overdue_books,
        name="overdue_books"
    ),
]