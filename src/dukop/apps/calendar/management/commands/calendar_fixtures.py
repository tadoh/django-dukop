"""
For development purposes: Create a bunch of random events at random times.
"""
import json
import random
import sys
import traceback
from datetime import timedelta

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from django.utils import timezone
from dukop.apps.calendar import models


LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."


def random_event_name():
    """
    Events of type {adverb} {thing} {proposition} {purpose}
    """
    adverbs = [
        "Great",
        "Pretty okay",
        "Unique",
        "Boring",
        "Intellectual",
        "Pretentious",
        "Blocking",
        "Delicious",
    ]
    things = [
        "gathering",
        "party",
        "surprise",
        "game",
        "dinner",
        "hackathon",
        "pet swap",
        "workshop",
        "role-play",
        "flash mob",
        "celebartion",
    ]
    propositions = [
        "in order to",
        "for",
        "by",
        "underneath",
        "to stop",
        "that will",
    ]
    purposes = [
        "bring peace",
        "wellness for everyone",
        "inner balance",
        "restore equality",
        "prove that nihilism is true",
        "make nice",
        "be great",
    ]

    return "{adverb} {thing} {proposition} {purpose}".format(
        adverb=random.choice(adverbs),
        thing=random.choice(things),
        proposition=random.choice(propositions),
        purpose=random.choice(purposes),
    )


def random_venue():
    return random.choice(
        [
            "Vakmærket",
            "Unghomsduset",
            "Holkets Fus",
            "Hådruspladsen",
        ]
    )


IMAGES = []


def random_image():
    global IMAGES
    image_width = 1024

    url = (
        "http://commons.wikimedia.org/w/api.php"
        "?action=query&generator=random"
        "&grnnamespace=6"
        "&prop=imageinfo"
        "&iiprop=url"
        "&iiurlwidth={}"
        "&format=json"
    ).format(image_width)

    print(url)

    if len(IMAGES) < 10:
        r = requests.get(url)
        data = json.loads(r.content)
        image_url = data["query"]["pages"][list(data["query"]["pages"].keys())[0]][
            "imageinfo"
        ][0]["thumburl"]
        print(image_url)
        r = requests.get(image_url)
        IMAGES.append(r.content)
        return r.content
    return random.choice(IMAGES)


class Command(BaseCommand):
    help = "Create test data"

    def add_arguments(self, parser):
        # Positional arguments are standalone name
        # parser.add_argument('store_id')

        parser.add_argument(
            "--max-per-day",
            type=int,
            default=5,
            help="Maximum amount (0-max) created per day",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=10,
            help="Number of days from now and into future",
        )

    @transaction.atomic
    def handle(self, *args, **options):

        no_days = options["days"]
        max_per_day = options["max_per_day"]
        try:
            self.stdout.write("Starting to import")

            for n in range(no_days):

                for __ in range(random.choice(range(1, max_per_day))):

                    start = (timezone.now() + timedelta(days=n)).replace(
                        hour=0, minute=0, second=0
                    )
                    end = (
                        timezone.now()
                        + timedelta(days=n + random.choice([0, 0, 0, 0, 0, 1]))
                    ).replace(hour=0, minute=0, second=0)

                    start += timedelta(hours=random.choice(range(0, 24)))
                    start += timedelta(minutes=random.choice([0, 0, 15, 30, 30, 45]))
                    end += timedelta(hours=random.choice(range(0, 24)))
                    end += timedelta(minutes=random.choice([0, 0, 15, 30, 30, 45]))

                    event = models.Event.objects.create(
                        published=True,
                        featured=random.choice(
                            [False, False, False, False, False, True]
                        ),
                        name=random_event_name(),
                        description=LOREM_IPSUM,
                        short_description=LOREM_IPSUM[:100],
                        venue_name=random_venue(),
                    )
                    models.EventTime.objects.create(
                        event=event,
                        start=start,
                        end=end,
                        comment="This is a randomly generated time",
                    )

                    if random.choice([True, False]):
                        image_data = random_image()
                        event_image = models.EventImage(event=event)
                        event_image.image.save("jpeg", ContentFile(image_data))
                        event_image.save()

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
