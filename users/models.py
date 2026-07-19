from django.conf import settings
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class AuthorProfile(models.Model):
    """Author identity linked to a Django user for API submissions."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_profile",
    )
    display_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    is_approved = models.BooleanField(
        default=False,
        help_text="Only approved authors may submit works through the API.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("user"),
        FieldPanel("display_name"),
        FieldPanel("bio"),
        FieldPanel("is_approved"),
    ]

    class Meta:
        ordering = ["display_name"]
        verbose_name = "author profile"
        verbose_name_plural = "author profiles"

    def __str__(self) -> str:
        status = "approved" if self.is_approved else "pending"
        return f"{self.display_name} ({status})"
