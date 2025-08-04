from django.db import models


class InboxItem(models.Model):
    list_name = models.CharField(max_length=100, default="lokalna_lista")
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} (Processed: {self.is_processed})"
