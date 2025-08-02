from django.contrib import admin

from inboxlist.models import InboxItem


@admin.register(InboxItem)
class InboxItemAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "is_processed")
    search_fields = ("title",)
    list_filter = ("is_processed",)
    ordering = ("-created_at",)
