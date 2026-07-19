import django_filters

from .models import Book, BookStatus


class PublishedBookFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name="genres__slug", lookup_expr="exact")
    author = django_filters.NumberFilter(field_name="authors__id")
    q = django_filters.CharFilter(method="filter_q")

    class Meta:
        model = Book
        fields = ["genre", "author"]

    def filter_q(self, queryset, name, value):
        return queryset.filter(title__icontains=value).distinct()


class AuthorBookFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=BookStatus.choices)

    class Meta:
        model = Book
        fields = ["status"]
