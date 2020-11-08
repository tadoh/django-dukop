import sys
import traceback

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from dukop.apps.sync_old import models


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
            help="Delete store instead of cleaning it up",
        )

    def handle(self, *args, **options):

        try:
            with transaction.atomic():
                self.stdout.write("Starting command execution")

                events = models.Events.objects.all()

                for event in events:
                    print(event)

                self.stdout.write("Command execution completed\n".format())

                if options.get("dry"):
                    transaction.rollback()
                else:
                    transaction.commit()

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
