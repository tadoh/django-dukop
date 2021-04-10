from datetime import timedelta

from django import template

from .. import models
from .. import utils

register = template.Library()


@register.simple_tag
def get_event_times(
    from_date=None,
    to_date=None,
    days=None,
    max_count=100,
    featured=None,
    published=True,
    has_image=None,
):

    lookup = {"event__published": published}

    if not from_date:
        from_date = utils.get_now()
    if days:
        to_date = from_date + timedelta(days=days)

    if from_date:
        lookup["end__gte"] = from_date
    if to_date:
        lookup["start__lt"] = to_date

    if featured is not None:
        lookup["event__featured"] = bool(featured)

    if has_image is not None:
        if has_image:
            lookup["event__images__id__gte"] = 0
        else:
            lookup["event__images"] = None

    return (
        models.EventTime.objects.filter(**lookup)
        .select_related("event")
        .prefetch_related("event__images", "event__links")
    ).distinct()[:max_count]


@register.simple_tag
def event_timeline_properties(event_time, now=None):
    """
    Properties to be used by the timeline filter
    """

    if not now:
        now = utils.get_now()

    hours_x_min = 8
    hours_x_max = 24
    hours_x = hours_x_max - hours_x_min

    if event_time.start < now or event_time.start.hour < hours_x_min:
        x_start = hours_x_min
    else:
        x_start = event_time.start.hour + (event_time.start.minute / 60.0)

    if event_time.end.date() > now.date():
        x_end = hours_x_max
    else:
        x_end = event_time.end.hour + (event_time.end.minute / 60.0)

    x_start_pct = 100.0 * float(x_start - hours_x_min) / hours_x
    x_end_pct = 100.0 * float(x_end - hours_x_min) / hours_x

    width_pct = x_end_pct - x_start_pct

    return {
        "x_start_pct": x_start_pct,
        "x_end_pct": x_end_pct,
        "width_pct": width_pct,
    }
