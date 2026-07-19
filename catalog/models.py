from django.db import models
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet


class BookStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING_REVIEW = "pending_review", "Pending review"
    PUBLISHED = "published", "Published"
    REJECTED = "rejected", "Rejected"


@register_snippet
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


@register_snippet
class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    synopsis = models.TextField(blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=32,
        choices=BookStatus.choices,
        default=BookStatus.DRAFT,
        db_index=True,
    )
    genres = models.ManyToManyField("catalog.Genre", blank=True, related_name="books")
    authors = models.ManyToManyField(
        "users.AuthorProfile",
        blank=True,
        related_name="books",
    )
    submitted_by = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="submitted_books",
    )
    cover_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("slug"),
                FieldPanel("synopsis"),
                FieldPanel("isbn"),
                FieldPanel("publication_year"),
                FieldPanel("status"),
            ],
            heading="Book details",
        ),
        FieldPanel("genres"),
        FieldPanel("authors"),
        FieldPanel("submitted_by"),
        FieldPanel("cover_image"),
    ]

    class Meta:
        ordering = ["-updated_at", "title"]

    def __str__(self) -> str:
        return f"{self.title} [{self.status}]"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "book"
            candidate = base
            counter = 2
            while Book.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{counter}"
                counter += 1
            self.slug = candidate
        super().save(*args, **kwargs)
