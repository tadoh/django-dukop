import os
import uuid

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


def image_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("uploads/events", filename)


class Event(models.Model):
    """
    Recurrence:

    TODO: For events that have an interval set for future repetition, we need a
    way to capture all exceptions.

    Calendars have "Edit this occurrence" or "Edit all occurrences"

    Likewise, we also need a way for events that have occurred to remain
    untouched, while future events can be edited.

    https://github.com/bmoeskau/Extensible/blob/master/recurrence-overview.md
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )
    short_description = models.TextField(
        blank=True,
        verbose_name=_("short description"),
        help_text=_(
            "A special short version of the event description, leave blank to auto-generate. Text-only, no Markdown."
        ),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_(
            "Enter details, which will be displayed on the event's own page. You can use Markdown."
        ),
    )

    slug = models.SlugField(
        null=True,
        blank=True,
        verbose_name=_("slug"),
        help_text=_("The part of a URL that is displayed in dukop.dk/event/<slug>/"),
    )

    host = models.ForeignKey(
        "users.Group",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="events",
        help_text=_(
            "A group may host an event and be displayed as the author of the event text."
        ),
    )

    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=False)

    is_cancelled = models.BooleanField(default=False)

    # What is this?
    show_nb = models.BooleanField(default=False)

    venue_name = models.CharField(
        max_length=255,
        verbose_name=_("venue name"),
        blank=True,
        null=True,
        help_text=_("If left blank, will be copied from host group"),
    )
    street = models.CharField(
        max_length=255,
        verbose_name=_("street"),
        blank=True,
        null=True,
        help_text=_("If left blank, will be copied from host group"),
    )
    city = models.CharField(
        max_length=255,
        verbose_name=_("city"),
        blank=True,
        null=True,
        help_text=_("If left blank, will be copied from host group"),
    )
    zip_code = models.CharField(
        verbose_name=_("zip code"),
        blank=True,
        null=True,
        max_length=16,
        help_text=_("If left blank, will be copied from host group"),
    )

    interval = models.ForeignKey(
        "Interval",
        on_delete=models.PROTECT,
        help_text=_("Repeats the event at some interval"),
        null=True,
        blank=True,
        related_name="events",
    )

    interval_exception = models.BooleanField(
        default=False,
        verbose_name=_("exception"),
        help_text=_(
            "If true, changes to other events in the interval should not effect this event, as it is marked as an exception"
        ),
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    owner_user = models.ForeignKey(
        "users.User",
        verbose_name=_("owner (user)"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_events",
    )
    owner_group = models.ForeignKey(
        "users.Group",
        verbose_name=_("owner (group)"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_events",
    )

    edit_secret = models.CharField(
        max_length=255,
        verbose_name=_("edit secret"),
        blank=True,
        null=True,
        editable=False,
    )

    view_secret = models.CharField(
        max_length=255,
        verbose_name=_("view secret"),
        blank=True,
        null=True,
        editable=False,
    )

    class Meta:
        verbose_name = _("Event")

    def save(self, *args, **kwargs):
        """
        Auto-populates the slug field if it isn't filled in.
        """
        if not self.pk:
            if not self.slug:
                self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class EventTime(models.Model):
    """
    Allows an event to take place at many different times
    """

    event = models.ForeignKey(Event, related_name="times", on_delete=models.CASCADE)
    start = models.DateTimeField(
        verbose_name=_("start"),
    )
    end = models.DateTimeField(
        verbose_name=_("end"),
        blank=True,
        null=True,
    )
    comment = models.CharField(
        max_length=255,
        verbose_name=_("comment"),
        help_text=_("Leave blank and nothing will be shown to readers"),
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Event time")
        ordering = ("start", "end")


class EventUpdate(models.Model):
    """
    An update can be posted by event owners and will be visible on the event
    page for users to see.
    """

    event = models.ForeignKey(Event, related_name="updates", on_delete=models.CASCADE)

    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Event update")
        ordering = ("created",)


class EventImage(models.Model):

    event = models.ForeignKey(Event, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(
        verbose_name=_("image"),
        help_text=_(
            "Allowed formats: JPEG, PNG, GIF. Please upload high resolution (>1000 pixels wide)."
        ),
        upload_to=image_upload_to,
    )
    priority = models.PositiveSmallIntegerField(
        default=0, help_text=_("0=first, 1=second etc.")
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("priority",)


class EventLink(models.Model):
    """
    Links have automatically generated labels, in this way we can
    potentially translate them or make them consistent. For instance,
    we can make Facebook links display with a warning.
    """

    event = models.ForeignKey(Event, related_name="links", on_delete=models.CASCADE)
    link = models.URLField(blank=True, null=True)
    priority = models.PositiveSmallIntegerField(
        default=0, help_text=_("0=first, 1=second etc.")
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Interval(models.Model):
    """
    A great resource here is RRULE for iCal format:

    https://www.kanzaki.com/docs/ical/rrule.html
    """

    weekday = models.ForeignKey("Weekday", on_delete=models.CASCADE)

    every_week = models.BooleanField(default=False)
    biweekly_even = models.BooleanField(default=False)
    biweekly_odd = models.BooleanField(default=False)
    first_week_of_month = models.BooleanField(default=False)
    second_week_of_month = models.BooleanField(default=False)
    third_week_of_month = models.BooleanField(default=False)
    last_week_of_month = models.BooleanField(default=False)

    starts = models.DateTimeField(null=True, blank=True)
    ends = models.DateTimeField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Weekday(models.Model):

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )
    number = models.PositiveSmallIntegerField(default=0, unique=True)
