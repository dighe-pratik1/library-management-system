from django.urls import path
from . import views


urlpatterns = [

    # ==========================
    # BOOKS
    # ==========================

    path(
        "",
        views.book_list,
        name="book_list"
    ),

    path(
        "add/",
        views.book_add,
        name="book_add"
    ),

    path(
        "<int:pk>/edit/",
        views.book_edit,
        name="book_edit"
    ),

    path(
        "<int:pk>/delete/",
        views.book_delete,
        name="book_delete"
    ),


    # ==========================
    # AUTHORS
    # ==========================

    path(
        "authors/",
        views.author_list,
        name="author_list"
    ),

    path(
        "authors/add/",
        views.author_add,
        name="author_add"
    ),

    path(
        "authors/<int:pk>/edit/",
        views.author_edit,
        name="author_edit"
    ),

    path(
        "authors/<int:pk>/delete/",
        views.author_delete,
        name="author_delete"
    ),


    # ==========================
    # PUBLISHERS
    # ==========================

    path(
        "publishers/",
        views.publisher_list,
        name="publisher_list"
    ),

    path(
        "publishers/add/",
        views.publisher_add,
        name="publisher_add"
    ),

    path(
        "publishers/<int:pk>/edit/",
        views.publisher_edit,
        name="publisher_edit"
    ),

    path(
        "publishers/<int:pk>/delete/",
        views.publisher_delete,
        name="publisher_delete"
    ),


    # ==========================
    # CATEGORIES
    # ==========================

    path(
        "categories/",
        views.category_list,
        name="category_list"
    ),

    path(
        "categories/add/",
        views.category_add,
        name="category_add"
    ),

    path(
        "categories/<int:pk>/edit/",
        views.category_edit,
        name="category_edit"
    ),

    path(
        "categories/<int:pk>/delete/",
        views.category_delete,
        name="category_delete"
    ),


    # ==========================
    # BOOK COPIES
    # ==========================

    path(
        "copies/",
        views.book_copy_list,
        name="book_copy_list"
    ),

    path(
        "copies/add/",
        views.book_copy_add,
        name="book_copy_add"
    ),

    path(
        "copies/<int:pk>/edit/",
        views.book_copy_edit,
        name="book_copy_edit"
    ),

    path(
        "copies/<int:pk>/delete/",
        views.book_copy_delete,
        name="book_copy_delete"
    ),
]