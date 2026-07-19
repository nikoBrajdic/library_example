from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied

from users.models import AuthorProfile

from .filters import AuthorBookFilter, PublishedBookFilter
from .models import Book, BookStatus
from .permissions import IsApprovedAuthor
from .serializers import (
    AuthorBookWriteSerializer,
    AuthorPublicSerializer,
    BookDetailSerializer,
    BookListSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="List published books"),
    retrieve=extend_schema(summary="Retrieve a published book by slug"),
)
class PublicBookViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    lookup_field = "slug"
    filterset_class = PublishedBookFilter
    search_fields = ["title", "synopsis"]
    ordering_fields = ["title", "publication_year", "updated_at"]
    ordering = ["title"]

    def get_queryset(self):
        return (
            Book.objects.filter(status=BookStatus.PUBLISHED)
            .prefetch_related("authors", "genres")
            .select_related("cover_image")
            .distinct()
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookDetailSerializer
        return BookListSerializer


@extend_schema_view(
    list=extend_schema(summary="List approved authors"),
    retrieve=extend_schema(summary="Retrieve an approved author"),
)
class PublicAuthorViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AuthorPublicSerializer
    search_fields = ["display_name", "bio"]
    ordering_fields = ["display_name"]
    ordering = ["display_name"]

    def get_queryset(self):
        return AuthorProfile.objects.filter(is_approved=True)


@extend_schema_view(
    list=extend_schema(summary="List my submitted books"),
    create=extend_schema(summary="Submit a new book for review"),
    partial_update=extend_schema(summary="Update one of my non-published books"),
    retrieve=extend_schema(summary="Retrieve one of my submitted books"),
)
class AuthorBookViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsApprovedAuthor]
    serializer_class = AuthorBookWriteSerializer
    filterset_class = AuthorBookFilter
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return (
            Book.objects.filter(submitted_by=self.request.user)
            .prefetch_related("genres", "authors")
            .order_by("-updated_at")
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.status == BookStatus.PUBLISHED:
            raise PermissionDenied("Published books cannot be edited by authors.")
        if instance.submitted_by_id != self.request.user.id:
            raise PermissionDenied("You may only edit your own submissions.")
        serializer.save()
