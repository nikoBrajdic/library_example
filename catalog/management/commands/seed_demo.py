from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Book, BookStatus, Genre
from users.models import AuthorProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo admin, authors, genres, and sample books."

    @transaction.atomic
    def handle(self, *args, **options):
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("adminpass")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin / adminpass"))
        else:
            self.stdout.write("Admin user already exists")

        niko_user, created = User.objects.get_or_create(
            username="niko",
            defaults={
                "email": "niko@example.com",
                "first_name": "Niko",
                "last_name": "Brajdić",
                "is_staff": False,
                "is_superuser": False,
            },
        )
        if created:
            niko_user.set_password("authorpass")
            niko_user.save()
            self.stdout.write(self.style.SUCCESS("Created niko / authorpass"))
        else:
            if niko_user.is_staff or niko_user.is_superuser:
                niko_user.is_staff = False
                niko_user.is_superuser = False
                niko_user.save(update_fields=["is_staff", "is_superuser"])
            self.stdout.write("Niko user already exists")

        niko_profile, _ = AuthorProfile.objects.update_or_create(
            user=niko_user,
            defaults={
                "display_name": "Niko Brajdić",
                "bio": (
                    "Biologist and software developer. Approved to submit works via API."
                ),
                "is_approved": True,
            },
        )

        # Catalog authors (not used for API login; attributed on books).
        uncle_bob = self._author(
            username="unclebob",
            first_name="Robert",
            last_name="Martin",
            display_name="Robert C. Martin (Uncle Bob)",
            bio="Software craftsman; author of Clean Code and related works.",
        )
        dijkstra = self._author(
            username="dijkstra",
            first_name="Edsger",
            last_name="Dijkstra",
            display_name="Edsger W. Dijkstra",
            bio="Computer scientist; pioneer of structured programming and algorithms.",
        )
        darwin = self._author(
            username="darwin",
            first_name="Charles",
            last_name="Darwin",
            display_name="Charles Darwin",
            bio="Naturalist; formulated the theory of evolution by natural selection.",
        )
        venter = self._author(
            username="venter",
            first_name="Craig",
            last_name="Venter",
            display_name="J. Craig Venter",
            bio="Genomicist and biotechnologist; known for sequencing and synthetic biology.",
        )
        corey = self._author(
            username="corey",
            first_name="James",
            last_name="Corey",
            display_name="James S. A. Corey",
            bio=(
                "Pen name of Daniel Abraham and Ty Franck; authors of The Expanse novels."
            ),
        )
        farmer = self._author(
            username="farmer",
            first_name="Nancy",
            last_name="Farmer",
            display_name="Nancy Farmer",
            bio="Author of speculative fiction for young adults, including The House of the Scorpion.",
        )

        science, _ = Genre.objects.get_or_create(
            slug="science",
            defaults={"name": "Science"},
        )
        computing, _ = Genre.objects.get_or_create(
            slug="computing",
            defaults={"name": "Computing"},
        )
        biology, _ = Genre.objects.get_or_create(
            slug="biology",
            defaults={"name": "Biology"},
        )
        fiction, _ = Genre.objects.get_or_create(
            slug="fiction",
            defaults={"name": "Fiction"},
        )
        scifi, _ = Genre.objects.get_or_create(
            slug="science-fiction",
            defaults={"name": "Science fiction"},
        )

        # Famous works: 2 published, 2 pending.
        self._book(
            slug="clean-code",
            title="Clean Code: A Handbook of Agile Software Craftsmanship",
            synopsis=(
                "Pragmatic guidance on writing readable, maintainable software "
                "through craftsmanship, naming, functions, and refactoring."
            ),
            publication_year=2008,
            status=BookStatus.PUBLISHED,
            genres=[computing],
            authors=[uncle_bob],
        )
        self._book(
            slug="go-to-statement-considered-harmful",
            title="Go To Statement Considered Harmful",
            synopsis=(
                "Influential letter arguing that unrestricted goto obscures "
                "program structure and should be abandoned in favour of clearer control flow."
            ),
            publication_year=1968,
            status=BookStatus.PUBLISHED,
            genres=[computing],
            authors=[dijkstra],
        )
        self._book(
            slug="on-the-origin-of-species",
            title="On the Origin of Species",
            synopsis=(
                "Foundational work presenting evolution by means of natural selection "
                "and descent with modification."
            ),
            publication_year=1859,
            status=BookStatus.PENDING_REVIEW,
            genres=[science, biology],
            authors=[darwin],
        )
        self._book(
            slug="life-at-the-speed-of-light",
            title="Life at the Speed of Light",
            synopsis=(
                "Account of creating the first synthetic cell and the broader "
                "implications of digital biology and synthetic genomics."
            ),
            publication_year=2013,
            status=BookStatus.PENDING_REVIEW,
            genres=[science, biology],
            authors=[venter],
        )

        # Niko Brajdić — three academic works.
        self._book(
            slug="claviceps-purpurea-ergotizam-i-ergot-alkaloidi",
            title="Ražena glavica (Claviceps purpurea), ergotizam i ergot alkaloidi",
            synopsis=(
                "Završni rad (PMF, 2014): ekologija Claviceps purpurea, povijesni utjecaj "
                "ergotizma te farmakološka primjena ergot alkaloida. "
                "https://repozitorij.pmf.unizg.hr/object/pmf:2086"
            ),
            publication_year=2014,
            status=BookStatus.PUBLISHED,
            genres=[biology, science],
            authors=[niko_profile],
            submitted_by=niko_user,
        )
        self._book(
            slug="migratorni-putovi-rijecnog-galeba-prudinec",
            title=(
                "Migratorni putovi riječnog galeba Chroicocephalus ridibundus "
                "(Linnaeus, 1766) s odlagališta otpada Prudinec u Zagrebu"
            ),
            synopsis=(
                "Diplomski rad (PMF, 2017): migratorni putovi riječnog galeba "
                "vezani uz odlagalište otpada Prudinec u Zagrebu."
            ),
            publication_year=2017,
            status=BookStatus.PUBLISHED,
            genres=[biology, science],
            authors=[niko_profile],
            submitted_by=niko_user,
        )
        self._book(
            slug="aplikacija-za-ocjenjivanje-taekwondo-poomsae",
            title='Izrada aplikacije za ocjenjivanje taekwondo „poomsae“ natjecanja',
            synopsis=(
                "Završni rad (TVZ, 2019): Android aplikacija za ocjenjivanje "
                "taekwondo poomsae natjecanja."
            ),
            publication_year=2019,
            status=BookStatus.PENDING_REVIEW,
            genres=[computing],
            authors=[niko_profile],
            submitted_by=niko_user,
        )

        # James S. A. Corey — The Expanse (main novels).
        expanse = [
            (
                "leviathan-wakes",
                "Leviathan Wakes",
                2011,
                "First Expanse novel: ice hauler Jim Holden and detective Miller "
                "collide around a missing girl and a conspiracy that reaches Mars, Earth, and the Belt.",
            ),
            (
                "calibans-war",
                "Caliban's War",
                2012,
                "Earth, Mars, and the Belt struggle for control as a new protomolecule "
                "threat emerges on Ganymede.",
            ),
            (
                "abaddons-gate",
                "Abaddon's Gate",
                2013,
                "Humanity gathers at the Ring: an alien gateway whose opening forces "
                "rival factions into uneasy contact.",
            ),
            (
                "cibola-burn",
                "Cibola Burn",
                2014,
                "The first human colony beyond the Ring becomes a flashpoint between "
                "settlers, corporations, and alien ecology.",
            ),
            (
                "nemesis-games",
                "Nemesis Games",
                2015,
                "The Rocinante crew splits across the solar system as a radical "
                "faction strikes at the heart of Earth and Mars.",
            ),
            (
                "babylons-ashes",
                "Babylon's Ashes",
                2016,
                "War and politics reshape the system after the Free Navy's assault; "
                "Holden and allies chase a path to lasting order.",
            ),
            (
                "persepolis-rising",
                "Persepolis Rising",
                2017,
                "Thirty years on, a laconic empire returns from the colonies with "
                "technology that upends the balance of power.",
            ),
            (
                "tiamats-wrath",
                "Tiamat's Wrath",
                2019,
                "Resistance against Laconian rule deepens as ancient forces stir "
                "beyond human understanding.",
            ),
            (
                "leviathan-falls",
                "Leviathan Falls",
                2021,
                "The final confrontation over the fate of humanity, the gates, "
                "and whatever built them.",
            ),
        ]
        for slug, title, year, synopsis in expanse:
            self._book(
                slug=slug,
                title=title,
                synopsis=synopsis,
                publication_year=year,
                status=BookStatus.PUBLISHED,
                genres=[fiction, scifi],
                authors=[corey],
            )

        self._book(
            slug="the-house-of-the-scorpion",
            title="The House of the Scorpion",
            synopsis=(
                "A young clone growing up in a dystopian opium empire confronts "
                "identity, power, and what it means to be human."
            ),
            publication_year=2002,
            status=BookStatus.PUBLISHED,
            genres=[fiction, scifi],
            authors=[farmer],
        )

        # Drop earlier Ada Lovelace demo titles if present.
        Book.objects.filter(
            slug__in=[
                "notes-on-the-analytical-engine",
                "sketch-of-the-analytical-engine",
            ]
        ).delete()

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write("  Wagtail admin: /admin/  (admin / adminpass)")
        self.stdout.write("  Author API:    niko / authorpass")

    def _author(self, *, username, first_name, last_name, display_name, bio):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": f"{username}@example.com",
                "first_name": first_name,
                "last_name": last_name,
                "is_staff": False,
                "is_superuser": False,
            },
        )
        if created:
            user.set_unusable_password()
            user.save()
        profile, _ = AuthorProfile.objects.update_or_create(
            user=user,
            defaults={
                "display_name": display_name,
                "bio": bio,
                "is_approved": True,
            },
        )
        return profile

    def _book(
        self,
        *,
        slug,
        title,
        synopsis,
        publication_year,
        status,
        genres,
        authors,
        submitted_by=None,
    ):
        book, created = Book.objects.update_or_create(
            slug=slug,
            defaults={
                "title": title,
                "synopsis": synopsis,
                "publication_year": publication_year,
                "status": status,
                "submitted_by": submitted_by,
            },
        )
        book.genres.set(genres)
        book.authors.set(authors)
        verb = "Created" if created else "Updated"
        # Avoid Windows console UnicodeEncodeError on non-ASCII titles.
        self.stdout.write(self.style.SUCCESS(f"{verb} book [{status}]: {slug}"))
        return book
