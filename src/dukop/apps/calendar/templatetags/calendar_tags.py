from datetime import timedelta

from django import template

from .. import models
from .. import utils

register = template.Library()


@register.simple_tag
def get_event_times(from_date=None, to_date=None, days=None, max_count=100):

    lookup = {}

    if not from_date:
        from_date = utils.get_now()
    if days:
        to_date = from_date + timedelta(days=days)

    if from_date:
        lookup["end__gte"] = from_date
    if to_date:
        lookup["start__lt"] = to_date

    return (
        models.EventTime.objects.filter(**lookup)
        .select_related("event")
        .prefetch_related("event__images", "event__links")
    )[:max_count]
