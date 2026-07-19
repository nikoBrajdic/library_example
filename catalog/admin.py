from django.contrib import admin

from .models import Book, Genre


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "publication_year", "updated_at")
    list_filter = ("status", "genres")
    search_fields = ("title", "isbn", "synopsis")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("genres", "authors")
    raw_id_fields = ("submitted_by", "cover_image")
