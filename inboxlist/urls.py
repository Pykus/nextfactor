from django.urls import path
from .views import (
    inbox_list,
    add_item,
    toggle_processed,
    confirm_delete_modal,
    delete_item,
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
    path("delete/<int:pk>/", delete_item, name="delete_item"),
]
