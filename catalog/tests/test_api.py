from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import Book, BookStatus, Genre
from users.models import AuthorProfile

User = get_user_model()


class AuthorAccessTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="writer", password="pass12345")
        AuthorProfile.objects.filter(user=self.author).update(
            display_name="Writer",
            is_approved=True,
        )
        self.client = Client()

    def test_author_cannot_access_wagtail_admin(self):
        logged_in = self.client.login(username="writer", password="pass12345")
        self.assertTrue(logged_in)
        response = self.client.get("/admin/")
        # Non-staff users are redirected away from Wagtail admin.
        self.assertIn(response.status_code, {302, 403})


class PublicAndAuthorApiTests(APITestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Fiction", slug="fiction")
        self.author_user = User.objects.create_user(
            username="ada",
            password="authorpass",
            email="ada@example.com",
        )
        self.profile = AuthorProfile.objects.get(user=self.author_user)
        self.profile.display_name = "Ada"
        self.profile.is_approved = True
        self.profile.save()

        self.unapproved_user = User.objects.create_user(
            username="pending",
            password="authorpass",
        )
        AuthorProfile.objects.filter(user=self.unapproved_user).update(is_approved=False)

        self.published = Book.objects.create(
            title="Published Work",
            slug="published-work",
            synopsis="Visible publicly",
            status=BookStatus.PUBLISHED,
            submitted_by=self.author_user,
        )
        self.published.genres.add(self.genre)
        self.published.authors.add(self.profile)

        self.pending = Book.objects.create(
            title="Pending Work",
            slug="pending-work",
            synopsis="Not public yet",
            status=BookStatus.PENDING_REVIEW,
            submitted_by=self.author_user,
        )
        self.pending.authors.add(self.profile)

    def test_public_list_shows_only_published(self):
        url = reverse("public-book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item["title"] for item in response.data["results"]]
        self.assertEqual(titles, ["Published Work"])

    def test_public_detail_by_slug(self):
        url = reverse("public-book-detail", kwargs={"slug": "published-work"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["slug"], "published-work")

    def test_pending_book_not_public(self):
        url = reverse("public-book-detail", kwargs={"slug": "pending-work"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_approved_author_can_submit(self):
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "ada", "password": "authorpass"},
            format="json",
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")

        response = self.client.post(
            reverse("author-book-list"),
            {
                "title": "New Submission",
                "synopsis": "Fresh manuscript",
                "genre_ids": [self.genre.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], BookStatus.PENDING_REVIEW)
        book = Book.objects.get(id=response.data["id"])
        self.assertEqual(book.submitted_by, self.author_user)
        self.assertIn(self.profile, book.authors.all())

    def test_unapproved_author_cannot_submit(self):
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "pending", "password": "authorpass"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")
        response = self.client.post(
            reverse("author-book-list"),
            {"title": "Should Fail"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_cannot_patch_published_book(self):
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "ada", "password": "authorpass"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")
        response = self.client.patch(
            reverse("author-book-detail", kwargs={"pk": self.published.pk}),
            {"synopsis": "Rewrite"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
