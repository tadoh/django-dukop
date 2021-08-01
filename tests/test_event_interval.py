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
    recurrence = models.EventRecurrence.objects.create(
        event=single_event,
        event_time_anchor=single_event.times.first(),
        every_week=True,
    )
    recurrence.sync()
    # Because the first event is now(), we will always fit 53 events in 365 days
    expected_count = 365 // 7 + 1
    assert recurrence.times.all().count() == expected_count
    recurrence.sync()
    assert recurrence.times.all().count() == expected_count


@pytest.mark.django_db()
def test_create_biweekly_odd_interval(single_event):  # noqa
    """
    Create and test weekly intervals
    """
    recurrence = models.EventRecurrence.objects.create(
        event=single_event,
        event_time_anchor=single_event.times.first(),
        biweekly_odd=True,
    )
    recurrence.sync()
    assert recurrence.times.all().first() == single_event.times.all().first()
    if single_event.times.first().start.date().isocalendar()[1] % 2 == 0:
        expected_count = 365 // 14 + 1
    else:
        expected_count = 365 // 14
    assert recurrence.times.all().count() == expected_count
    recurrence.sync()
    assert recurrence.times.all().count() == expected_count


@pytest.mark.django_db()
def test_create_biweekly_even_interval(single_event):  # noqa
    """
    Create and test weekly intervals
    """
    recurrence = models.EventRecurrence.objects.create(
        event=single_event,
        event_time_anchor=single_event.times.first(),
        biweekly_even=True,
    )
    recurrence.sync()
    assert recurrence.times.all().first() == single_event.times.all().first()
    if single_event.times.first().start.date().isocalendar()[1] % 2 == 0:
        expected_count = 365 // 14 + 1
    else:
        expected_count = 365 // 14
    assert recurrence.times.all().count() == expected_count
    recurrence.sync()
    assert recurrence.times.all().count() == expected_count
