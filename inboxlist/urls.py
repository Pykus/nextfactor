from django.urls import path
from .views import (
    edit_item,
    inbox_list,
    add_item,
    toggle_processed,
    confirm_delete_modal,
    delete_item,
    update_item,
)

urlpatterns = [
    path("", inbox_list, name="inbox_list"),
    path("add/", add_item, name="add_item"),
    path("toggle/<int:pk>/", toggle_processed, name="toggle_processed"),
    path(
        "confirm-delete/<int:pk>/",
        confirm_delete_modal,
        name="confirm_delete_modal",
    ),
    path("edit/<int:pk>/", edit_item, name="edit_item"),
    path("update/<int:pk>/", update_item, name="update_item"),
    path("delete/<int:pk>/", delete_item, name="delete_item"),
]
