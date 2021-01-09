import os
import sys
import traceback
from datetime import datetime

import pytz
from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from django.utils import timezone
from dukop.apps.calendar.models import Event
from dukop.apps.calendar.models import EventImage
from dukop.apps.calendar.models import EventTime
from dukop.apps.calendar.models import Interval
from dukop.apps.calendar.models import Weekday
from dukop.apps.sync_old import models
from dukop.apps.users.models import Group


bad_fks = 0


# Gets the number from weekday strings used in old db
weekday_numbers = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


# Map between old EventSeries and new Interval
event_series_interval_map = {}


def df(value):
    """
    Converts a UTC non-timezone aware field to current timezone.
    This is because the old system somehow didn't put timezone information
    in datetime fields.
    """
    return (
        timezone.localtime(
            value.replace(tzinfo=pytz.UTC), pytz.timezone(settings.TIME_ZONE)
        )
        if value
        else None
    )


def create_interval(event_series):
    """
    Creates an Interval from old EventSeries object
    """
    if event_series:
        days = event_series.days.split(",")
        if len(days) > 1:
            print("WARNING: Several weekdays in an EventSeries")
        return Interval.objects.create(
            weekday=Weekday.objects.get(number=weekday_numbers[days[0]]),
            every_week=bool(event_series.rule == "weekly"),
            biweekly_even=bool(event_series.rule == "biweekly_even"),
            biweekly_odd=bool(event_series.rule == "biweekly_odd"),
            first_week_of_month=bool(event_series.rule == "first"),
            second_week_of_month=bool(event_series.rule == "second"),
            third_week_of_month=bool(event_series.rule == "third"),
            last_week_of_month=bool(event_series.rule == "last"),
            starts=datetime.combine(event_series.start_date, event_series.start_time),
            ends=datetime.combine(event_series.expiry, event_series.end_time),
        )


def ensure_location_exists(old_event):
    global bad_fks
    try:
        if old_event.location and old_event.location.name:
            pass
    except models.Locations.DoesNotExist:
        print("A location had a bad FK")
        bad_fks += 1
        old_event.location = None


def create_group(old_event):
    if not old_event.location or not old_event.location.name:
        return None
    return Group.objects.create(
        name=old_event.location.name,
        street=old_event.location.street_address,
        zip_code=old_event.location.postcode,
        city=old_event.location.town,
        description=old_event.location.description,
        link1=old_event.location.link,
        is_restricted=True,
    )


def create_event(old_event, group, interval):

    event = Event(
        name=old_event.title,
        short_description=old_event.short_description or "",
        description=old_event.long_description or "",
        is_cancelled=bool(old_event.cancelled),
        created=old_event.created_at,
        host=group,
        interval=interval,
    )
    if old_event.location:
        event.venue_name = old_event.location.name
        event.street = old_event.location.street_address
        event.zip_code = old_event.location.postcode
        event.city = old_event.location.town
    event.save()
    return event


def create_event_time(old_event, new_event):
    return EventTime.objects.create(
        event=new_event,
        start=df(old_event.start_time),
        end=df(old_event.end_time),
        created=old_event.created_at,
        modified=old_event.updated_at,
    )


not_found_images = 0


def import_image(old_event, new_event, old_folder):
    """
    Rails has saved images in weird subfolders.
    https://stackoverflow.com/questions/15494906/understanding-id-partition-in-paperclip
    paperclip id_partition method prepend '0' to ID of ActiveRecord instance to make it of length 9 characters.

    i.e 12 would be converted to 000000012, then it simply splits this string into three chunks and joins these chunks with /
    """

    global not_found_images
    subfolders = str(old_event.id).zfill(9)
    subfolders = (
        old_folder,
        subfolders[0:3],
        subfolders[3:6],
        subfolders[6:9],
        "original",
    )
    image_path = os.path.join(
        *subfolders,
        old_event.picture_file_name,
    )
    try:
        image_data = ImageFile(open(image_path, "rb").read())
        event_image = EventImage(event=new_event)
        event_image.image = image_data
        event_image.save()
        print("Found image {}".format(old_event.picture_file_name))
    except FileNotFoundError:
        not_found_images += 1
        print(
            "Did not find {}\ntotal images not found: {}".format(
                image_path, not_found_images
            )
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
        parser.add_argument(
            "import_img_dir",
            type=str,
            help="Base where old images are found",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        global event_series_interval_map

        import_base_dir = options.get("import_img_dir")

        try:
            self.stdout.write("Starting to import")

            event_series = models.EventSeries.objects.all()

            for series in event_series:

                # 2. Sync EventSeries if it does not exist
                interval = create_interval(series)
                event_series_interval_map[series.id] = interval

            # Debugging: Just process 10 objects.
            events = models.Events.objects.all()

            for event in events:
                self.stdout.write("-----------------------------")
                ensure_location_exists(event)

                # 1. Create a Group from the old Location
                group = create_group(event)

                # 2. Create Event
                new_event = create_event(event, group, interval)

                # 3. Interval
                if event.event_series_id in event_series_interval_map:
                    new_event.interval = event_series_interval_map[
                        event.event_series_id
                    ]

                # 4. EventTime
                if event.start_time:
                    create_event_time(event, new_event)
                else:
                    self.stderr.write(
                        "Old event has no start time? title: {}, id: {}".format(
                            event.short_description, event.id
                        )
                    )

                # 5. EventImage
                if event.picture_file_name:
                    import_image(event, new_event, import_base_dir)

                # 6. EventLink

                print(event.title)
                # print(event.picture_file_name)
                # print(event.short_description)
                # print(event.long_description)
                # print(df(event.start_time))
                # print(df(event.end_time))
                # print(event.link)
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
