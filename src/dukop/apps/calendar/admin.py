from django.contrib import admin
from django.template.defaultfilters import truncatewords
from django.utils.safestring import SafeText
from django.utils.translation import gettext_lazy as _

from . import models


@admin.register(models.Sphere)
class SphereAdmin(admin.ModelAdmin):
    pass


class EventTimeInline(admin.TabularInline):
    model = models.EventTime
    raw_id_fields = ("recurrence",)


class EventImageInlineAdmin(admin.TabularInline):
    model = models.EventImage


class EventLinkInlineAdmin(admin.TabularInline):
    model = models.EventLink


class EventRecurrenceInlineAdmin(admin.TabularInline):
    model = models.EventRecurrence
    raw_id_fields = ("event_time_anchor",)


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "show_times",
        "venue_name",
        "short_description_truncated",
        "event_image",
    )
    list_filter = ("featured", "published", "is_cancelled", "times__start")
    raw_id_fields = ("host",)
    inlines = [
        EventTimeInline,
        EventRecurrenceInlineAdmin,
        EventImageInlineAdmin,
        EventLinkInlineAdmin,
    ]
    search_fields = (
        "name",
        "venue_name",
    )

    def short_description_truncated(self, instance):
        return truncatewords(instance.short_description, 100)

    short_description_truncated.short_description = _("short description")

    def show_times(self, instance):
        html = SafeText("<br>".join(str(time) for time in instance.times.all()))
        if not html:
            html = "None"
        return html

    show_times.short_description = _("time(s)")

    def event_image(self, instance):
        image = instance.images.first()
        if image:
            return SafeText(
                """<img src="{}" alt="Event image" />""".format(image.thumb().url)
            )

    event_image.short_description = "Photo"


@admin.register(models.EventRecurrence)
class EventRecurrenceAdmin(admin.ModelAdmin):
    raw_id_fields = ("event", "event_time_anchor")
    list_display = ("event", "end")
    list_filter = ("end",)
    search_fields = ("event__name",)
