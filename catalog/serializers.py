from django.utils.text import slugify
from rest_framework import serializers

from users.models import AuthorProfile

from .models import Book, BookStatus, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name", "slug")


class AuthorPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorProfile
        fields = ("id", "display_name", "bio")


class BookListSerializer(serializers.ModelSerializer):
    authors = AuthorPublicSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "slug",
            "synopsis",
            "isbn",
            "publication_year",
            "status",
            "authors",
            "genres",
            "created_at",
            "updated_at",
        )


class BookDetailSerializer(BookListSerializer):
    cover_image_url = serializers.SerializerMethodField()

    class Meta(BookListSerializer.Meta):
        fields = BookListSerializer.Meta.fields + ("cover_image_url",)

    def get_cover_image_url(self, obj):
        if not obj.cover_image:
            return None
        request = self.context.get("request")
        url = obj.cover_image.file.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class AuthorBookWriteSerializer(serializers.ModelSerializer):
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        source="genres",
        required=False,
    )

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "slug",
            "synopsis",
            "isbn",
            "publication_year",
            "genre_ids",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")
        extra_kwargs = {
            "slug": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        genres = validated_data.pop("genres", [])
        request = self.context["request"]
        profile = request.user.author_profile

        slug = validated_data.get("slug") or slugify(validated_data["title"]) or "book"
        validated_data["slug"] = self._unique_slug(slug)
        validated_data["status"] = BookStatus.PENDING_REVIEW
        validated_data["submitted_by"] = request.user

        book = Book.objects.create(**validated_data)
        if genres:
            book.genres.set(genres)
        book.authors.set([profile])
        return book

    def update(self, instance, validated_data):
        genres = validated_data.pop("genres", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if not instance.slug:
            instance.slug = self._unique_slug(slugify(instance.title) or "book", exclude_pk=instance.pk)
        instance.save()
        if genres is not None:
            instance.genres.set(genres)
        return instance

    def _unique_slug(self, base: str, exclude_pk=None) -> str:
        candidate = base
        counter = 2
        qs = Book.objects.all()
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        while qs.filter(slug=candidate).exists():
            candidate = f"{base}-{counter}"
            counter += 1
        return candidate
