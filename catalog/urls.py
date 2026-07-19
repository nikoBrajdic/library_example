from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthorBookViewSet, PublicAuthorViewSet, PublicBookViewSet

router = DefaultRouter()
router.register(r"books", PublicBookViewSet, basename="public-book")
router.register(r"authors", PublicAuthorViewSet, basename="public-author")
router.register(r"author/books", AuthorBookViewSet, basename="author-book")

urlpatterns = [
    path("", include(router.urls)),
]
