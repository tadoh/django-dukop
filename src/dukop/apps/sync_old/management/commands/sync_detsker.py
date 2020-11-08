import sys
import traceback

import pytz
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from django.utils import timezone
from dukop.apps.calendar.models import Event
from dukop.apps.sync_old import models
from dukop.apps.users.models import Group


def df(value):
    """
    Converts a UTC non-timezone aware field to current timezone.
    This is because the old system somehow didn't put timezone information
    in datetime fields.
    """
    return timezone.localtime(
        value.replace(tzinfo=pytz.UTC), pytz.timezone(settings.TIME_ZONE)
    )


def create_interval(old_event):
    if not old_event.event_series:
        return None


def create_group(old_event):
    if not old_event.locations or not old_event.locations.name:
        return None
    return Group.objects.create(
        name=old_event.locations.name,
        street=old_event.street_address,
        zip_code=old_event.postcode,
        city=old_event.town,
        description=old_event.description,
        link1=old_event.link,
        is_restricted=True,
    )


def create_event(old_event, group, interval):

    return Event.objects.create(
        name=old_event.title,
        short_description=old_event.short_description or "",
        description=old_event.long_description or "",
        host=group,
        interval=interval,
    )


class Command(BaseCommand):
    help = "Import stuff from old database"

    def add_arguments(self, parser):
        # Positional arguments are standalone name
        # parser.add_argument('store_id')

        # Named (optional) arguments start with --
        parser.add_argument(
            "--dry",
            action="store_true",
            default=False,
            help="Dry-run: About the whole database transaction at the end",
        )

    @transaction.atomic
    def handle(self, *args, **options):

        try:
            self.stdout.write("Starting to import")

            # Debugging: Just process 10 objects.
            events = models.Events.objects.all()[:10]

            for event in events:

                # 1. Create a Group from the old Location
                group = create_group(event)

                # 2. Sync EventSeries if it does not exist
                interval = create_interval(event)

                # 3. Create Event
                new_event = create_event(event, group, interval)

                # 4. EventTime

                # 5. EventImage

                # 6. EventLink

                print(event.title)
                print(event.short_description)
                print(event.long_description)
                print(df(event.start_time))
                print(df(event.end_time))
                print(event.created_at)
                print(event.price)
                print(event.cancelled)
                print(event.link)

                print(new_event)

            self.stdout.write("Command execution completed\n".format())

        except Exception as e:  # noqa
            exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted_excption = traceback.format_exception(
                exc_type, exc_value, exc_traceback
            )
            for line in formatted_excption:
                self.stdout.write(line, ending="")
            raise CommandError(
                "An exception occurred. All operations aborted, database rolled back.\n"
            )

        if options.get("dry"):
            raise CommandError("Dry-running so aborting transactions.")
