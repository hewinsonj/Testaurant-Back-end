from django.conf import settings
from django.db import models


class Restaurant(models.Model):
    # Core
    name       = models.CharField(max_length=255)
    city       = models.CharField(max_length=120, blank=True)
    state      = models.CharField(max_length=60, blank=True)

    # Nice-to-haves for search/filter
    address    = models.CharField(max_length=255, blank=True)
    zip_code   = models.CharField(max_length=20, blank=True)

    # Ownership / tenancy
    owner      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="restaurants_owned",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["city", "state"]),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        loc = f"{self.city}, {self.state}".strip(", ")
        return f"{self.name} ({loc})" if loc else self.name