from django.db.models.signals import post_save
from django.dispatch import receiver
from dukop.apps.users import email
from dukop.apps.users.models import User

from . import models


@receiver(post_save, sender=models.Event)
def event_created(**kwargs):
    event = kwargs.get("instance")
    created = kwargs.get("created", False)

    if created:
        if hasattr(event, "skip_admin_notifications"):
            return
        admins = {}
        for sphere in event.spheres.all():
            for user in sphere.admins.filter(is_active=True):
                admins[user.id] = user

        if event.spheres.all().count() == 0:
            admins = {
                user.id: user
                for user in User.objects.filter(is_superuser=True, is_active=True)
            }

        for user in admins.values():
            mail = email.AdminEventCreated(user=user, context={"event": event})
            mail.send()
