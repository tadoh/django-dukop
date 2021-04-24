from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext as _


def get_now():
    """
    This is the central function for determining what's past and present in the
    eyes of any function in the calendar. It is used to mimic the past in
    testing and development.
    """
    now = timezone.now()
    if hasattr(settings, "DUKOP_BACKWARDS_DAYS"):
        return now - timedelta(days=settings.DUKOP_BACKWARDS_DAYS)
    return now


def display_date(dtm):
    return date_format(dtm)


def display_time(dtm):
    return dtm.strftime("%H:%M")


def display_datetime(dtm):
    return _("{date} at {time}").format(date=date_format(dtm), time=display_time(dtm))


def populate_interval():
    pass
