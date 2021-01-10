from django.contrib import admin
from django.template.defaultfilters import truncatewords
from django.utils.safestring import SafeText
from django.utils.translation import gettext_lazy as _

from . import models


class EventTimeInline(admin.TabularInline):
    model = models.EventTime


class EventImageInlineAdmin(admin.TabularInline):
    model = models.EventImage


class EventLinkInlineAdmin(admin.TabularInline):
    model = models.EventLink


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
    inlines = [EventTimeInline, EventImageInlineAdmin, EventLinkInlineAdmin]
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


@admin.register(models.EventInterval)
class EventInvervalAdmin(admin.ModelAdmin):

    list_display = ("event", "starts", "ends")
    list_filter = ("starts", "ends")
