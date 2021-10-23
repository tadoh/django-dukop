from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.timezone import make_aware
from django.utils.translation import gettext as _


def get_now():
    """
    This is the central function for determining what's past and present in the
    eyes of any function in the calendar. It is used to mimic the past in
    testing and development.
    """
    now = timezone.localtime()
    if hasattr(settings, "DUKOP_BACKWARDS_DAYS"):
        return now - timedelta(days=settings.DUKOP_BACKWARDS_DAYS)
    return now


def display_date(dtm):
    return date_format(dtm)


def display_time(dtm):
    return timezone.localtime(dtm).strftime("%H:%M")


def display_datetime(dtm):
    return _("{date} at {time}").format(date=date_format(dtm), time=display_time(dtm))


def display_interval(start, end=None):
    """
    Displays an interval, something with a start and finish. Since having a
    finish isn't mandatory, it may be omitted silently.

    This can be made even more elegant.

    Remember that when changing formats, translations have to be updated, too.
    """
    if not end:
        return _("{start_date} at {start_time}").format(
            start_date=date_format(start), start_time=display_time(start)
        )
    elif end.date() == start.date():
        return _("{start_date} at {start_time} - {end_time}").format(
            start_date=date_format(start),
            start_time=display_time(start),
            end_time=display_time(end),
        )
    else:
        return _("{start_date} at {start_time} - {end_date} at {end_time}").format(
            start_date=date_format(start),
            end_date=date_format(end),
            start_time=display_time(start),
            end_time=display_time(end),
        )


def timedelta_naive(dtm1, **kwargs):
    return make_aware(datetime.combine(dtm1.date() + timedelta(**kwargs), dtm1.time()))
