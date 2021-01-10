from datetime import timedelta

from django import template

from .. import models
from .. import utils

register = template.Library()


@register.simple_tag
def get_event_times(from_date=None, to_date=None, days=None):

    if not from_date:
        from_date = utils.get_now()
    if days:
        to_date = from_date + timedelta(days=days)
    elif not to_date:
        to_date = from_date + timedelta(days=7)

    return (
        models.EventTime.objects.filter(end__gte=from_date, start__lt=to_date)
        .select_related("event")
        .prefetch_related("event__images", "event__links")
    )
