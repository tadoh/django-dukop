"""
For development purposes: Create a bunch of random events at random times.
"""
import json
import os
import random
import sys
import traceback
from datetime import timedelta

import requests
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from django.utils import timezone
from dukop.apps.calendar import models
from dukop.apps.news.models import NewsStory
from dukop.apps.users.models import Group
from dukop.apps.users.models import Location


LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

LOREM_IPSUM_MARKDOWN = "## Lorem ipsum dolor sit amet\n\nconsectetur adipiscing elit\n\n### Sed do eiusmod tempor incididunt\n\n [A silly link](https://dr.dk) ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."


def random_event_name():
    """
    Events of type {adverb} {thing} {proposition} {purpose}
    """
    adverbs = [
        "Great",
        "Pretty okay inspiring",
        "Unique",
        "Nihilistic",
        "Intellectual",
        "Pretentious",
        "Queer",
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
        "celebration",
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


def random_location():
    return random.choice(
        [
            "Vakmærket",
            "Unghomsduset",
            "Holkets Fus",
            "Hådruspladsen",
        ]
    )


def random_group():
    return random.choice(
        [
            "Marxist book club",
            "Punkaholics",
            "Queer nights",
            "Stop the System",
        ]
    )


IMAGES = []


def random_image(use_local=False):
    global IMAGES
    image_width = 1024

    if use_local:
        return open(
            os.path.join(os.path.dirname(__file__), "testphoto.jpg"), "rb"
        ).read()

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
        user_agent = {
            "User-agent": "DukOp/CalendarFixtures (https://github.com/dukop/django-dukop/; dukop@riseup.net) django-dukop/0.0"
        }
        r = requests.get(image_url, headers=user_agent)
        image_data = r.content
        if b"Wikimedia Error" in image_data:
            raise RuntimeError(
                "Oh no :(\n\n{}\n\nStopping to download because of Wikimedia error.".format(
                    image_data
                )
            )
        IMAGES.append(image_data)
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
        parser.add_argument(
            "--local-image",
            type=bool,
            default=False,
            help="Use the local test image, not from Wikimedia",
        )

    @transaction.atomic
    def handle(self, *args, **options):

        no_days = options["days"]
        max_per_day = options["max_per_day"]
        local_image = options.get("local_image", False)
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

                    location = Location.objects.get_or_create(name=random_location())[0]
                    group = Group.objects.get_or_create(name=random_group())[0]

                    event = models.Event.objects.create(
                        published=True,
                        featured=random.choice(
                            [False, False, False, False, False, True]
                        ),
                        name=random_event_name(),
                        description=LOREM_IPSUM,
                        short_description=LOREM_IPSUM[:100],
                        venue_name=location.name,
                        host=group,
                        location=location,
                    )
                    models.EventTime.objects.create(
                        event=event,
                        start=start,
                        end=end,
                        comment="This is a randomly generated time",
                    )

                    event.spheres.add(models.Sphere.get_default())

                    if random.choice([True, False]):
                        image_data = random_image(use_local=local_image)
                        event_image = models.EventImage(event=event)
                        event_image.image.save("jpeg", ContentFile(image_data))
                        event_image.save()

            if NewsStory.objects.all().count() == 0:
                self.stdout.write(
                    "No News stories found, so creating 2 of those, too...\n".format()
                )
                NewsStory.objects.create(
                    headline="Developers be having fun",
                    short_story="A developer is working hard right now!",
                    text=LOREM_IPSUM_MARKDOWN,
                    published=True,
                )
                NewsStory.objects.create(
                    headline="We think Django is great",
                    short_story="We used a web framework called Django this time. It's going great. Click to read more.",
                    text=LOREM_IPSUM_MARKDOWN,
                    published=True,
                    url="https://www.djangoproject.com/",
                )

            if Site.objects.filter(domain="example.com").exists():
                Site.objects.filter(domain="example.com").update(
                    domain="localhost:8000"
                )
                self.stdout.write(
                    self.style.SUCCESS("Changed example.com to localhost:8000")
                )

            self.stdout.write(self.style.SUCCESS("Created a bunch of example data"))

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
