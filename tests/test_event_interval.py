import pytest
from dukop.apps.calendar import models

from .fixtures_calendar import single_event  # noqa


@pytest.mark.django_db()
def test_weekdays():
    assert models.Weekday.objects.all().count() > 0


@pytest.mark.django_db()
def test_create_weekly_interval(single_event):  # noqa
    """
    Create and test weekly intervals
    """
    interval = models.EventInterval.objects.create(
        event=single_event,
        event_time_anchor=single_event.times.first(),
        every_week=True,
    )
    interval.sync()
    assert interval.times.all().count() == 365 // 7
    interval.sync()
    assert interval.times.all().count() == 365 // 7
