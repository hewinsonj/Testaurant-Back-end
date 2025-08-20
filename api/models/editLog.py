from django.db import models
from django.contrib.postgres.fields import ArrayField  # optional if you want arrays
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder


class EditLog(models.Model):
    # What was edited (kept simple & fast for querying)
    ITEM_TEST     = "Test"
    ITEM_QUESTION = "Question"
    ITEM_DRINK    = "Drink"
    ITEM_FOOD     = "Food"

    ITEM_TYPE_CHOICES = [
        (ITEM_TEST, "Test"),
        (ITEM_QUESTION, "Question"),
        (ITEM_DRINK, "Drink"),
        (ITEM_FOOD, "Food"),
    ]

    # How it changed
    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_DELETE = "delete"

    ACTION_CHOICES = [
        (ACTION_CREATE, "Create"),
        (ACTION_UPDATE, "Update"),
        (ACTION_DELETE, "Delete"),
    ]

    # Required fields (fast filters)
    item_type   = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    item_id     = models.PositiveIntegerField()  # id of the edited object
    action      = models.CharField(max_length=10, choices=ACTION_CHOICES, default=ACTION_UPDATE)

    # Who did it
    editor      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="edit_logs",
    )

    # Optional context (if you want to scope edits to a restaurant)
    restaurant  = models.ForeignKey(
        "Restaurant",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="edit_logs",
    )

    # Snapshots to make the log human-readable even if entities are later renamed/deleted
    item_name_snapshot   = models.CharField(max_length=255, blank=True)
    editor_name_snapshot = models.CharField(max_length=255, blank=True)

    # Flexible details about the change. Example shape:
    # {
    #   "before": {"name": "Old", "price": 12},
    #   "after":  {"name": "New", "price": 14},
    #   "fields_changed": ["name", "price"]
    # }
    changes     = models.JSONField(encoder=DjangoJSONEncoder, default=dict, blank=True)

    # When it happened
    edit_date   = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["item_type", "item_id"]),
            models.Index(fields=["edit_date"]),
        ]
        ordering = ["-edit_date"]

    def __str__(self) -> str:
        who = self.editor_name_snapshot or (self.editor.get_full_name() if self.editor else "Unknown")
        return f"[{self.edit_date:%Y-%m-%d %H:%M}] {who} {self.action} {self.item_type}#{self.item_id}"