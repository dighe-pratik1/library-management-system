from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.library_list,
        name="library_list"
    ),

    path(
        "add/",
        views.library_add,
        name="library_add"
    ),

    path(
        "edit/<int:pk>/",
        views.library_edit,
        name="library_edit"
    ),

    path(
        "delete/<int:pk>/",
        views.library_delete,
        name="library_delete"
    ),

]