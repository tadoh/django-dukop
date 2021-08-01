import calendar

import pytest
from dukop.apps.calendar import models

from .fixtures_calendar import single_event  # noqa


@pytest.mark.django_db()
def test_weekdays():
    assert models.Weekday.objects.all().count() > 0


@pytest.mark.django_db()
def test_create_weekly_recurrence(single_event):  # noqa
    """
    Create and test weekly recurrence
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
def test_create_biweekly_odd_recurrence(single_event):  # noqa
    """
    Create and test weekly recurrence
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
def test_create_biweekly_even_recurrence(single_event):  # noqa
    """
    Create and test weekly recurrence
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


@pytest.mark.django_db()
def test_create_first_week_of_month_recurrence(single_event):  # noqa
    """
    Create and test weekly recurrence
    """
    original_weekday = single_event.times.first().start.weekday()
    anchor_event_time = single_event.times.first()
    recurrence = models.EventRecurrence.objects.create(
        event=single_event,
        event_time_anchor=anchor_event_time,
        first_week_of_month=True,
    )
    recurrence.sync()

    # How many events fit in 365 days depends on how many days we are into the
    # current month
    expected_count = 13 if anchor_event_time.start.day > 7 else 12
    assert recurrence.times.all().first() == anchor_event_time
    for event_time in recurrence.times.all():
        print(event_time)
        assert event_time.start.weekday() == original_weekday
        if event_time != anchor_event_time:
            assert event_time.start.day < 8
    assert recurrence.times.all().count() == expected_count
    recurrence.sync()
    assert recurrence.times.all().count() == expected_count


@pytest.mark.django_db()
def test_create_second_week_of_month_recurrence(single_event):  # noqa
    """
    Create and test weekly recurrence
    """
    original_weekday = single_event.times.first().start.weekday()
    anchor_event_time = single_event.times.first()
    recurrence = models.EventRecurrence.objects.create(
        event=single_event,
        event_time_anchor=single_event.times.first(),
        second_week_of_month=True,
    )
    recurrence.sync()

    expected_count = 13 if anchor_event_time.start.day > 14 else 12
    assert recurrence.times.all().first() == anchor_event_time
    for event_time in recurrence.times.all():
        print(event_time)
        assert event_time.start.weekday() == original_weekday
        if event_time != anchor_event_time:
            assert event_time.start.day >= 8 < 15
    assert recurrence.times.all().count() == expected_count
    recurrence.sync()
    assert recurrence.times.all().count() == expected_count


@pytest.mark.django_db()
def test_create_third_week_of_month_recurrence(single_event):  # noqa
    """
    Create and test weekly recurrence
    """
    original_weekday = single_event.times.first().start.weekday()
    anchor_event_time = single_event.times.first()
    recurrence = models.EventRecurrence.objects.create(
        event=single_event,
        event_time_anchor=single_event.times.first(),
        third_week_of_month=True,
    )
    recurrence.sync()

    expected_count = 13 if anchor_event_time.start.day > 21 else 12
    assert recurrence.times.all().first() == anchor_event_time
    for event_time in recurrence.times.all():
        print(event_time)
        assert event_time.start.weekday() == original_weekday
        if event_time != anchor_event_time:
            assert event_time.start.day >= 14 < 22
    assert recurrence.times.all().count() == expected_count
    recurrence.sync()
    assert recurrence.times.all().count() == expected_count


@pytest.mark.django_db()
def test_last_day_of_month_recurrence(single_event):  # noqa
    """
    Create and test weekly recurrence
    """
    original_weekday = single_event.times.first().start.weekday()
    anchor_event_time = single_event.times.first()
    recurrence = models.EventRecurrence.objects.create(
        event=single_event,
        event_time_anchor=single_event.times.first(),
        last_week_of_month=True,
    )
    recurrence.sync()

    expected_count = 12
    assert recurrence.times.all().first() == anchor_event_time
    for event_time in recurrence.times.all():
        print(event_time)
        assert event_time.start.weekday() == original_weekday
        if event_time != anchor_event_time:
            __, last_day = calendar.monthrange(
                event_time.start.year, event_time.start.month
            )
            assert event_time.start.day > last_day - 7
    assert recurrence.times.all().count() == expected_count
    recurrence.sync()
    assert recurrence.times.all().count() == expected_count
