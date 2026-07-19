from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AuthorProfile

User = get_user_model()


@receiver(post_save, sender=User)
def ensure_author_profile(sender, instance, created, **kwargs):
    """
    Create a non-approved AuthorProfile for new non-staff users.

    Staff/admin accounts are CMS users and do not need an author profile by default.
    """
    if not created or instance.is_staff:
        return
    AuthorProfile.objects.get_or_create(
        user=instance,
        defaults={
            "display_name": instance.get_full_name() or instance.username,
            "is_approved": False,
        },
    )
