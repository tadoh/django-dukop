import pytz
from django.contrib.syndication.views import Feed
from django.urls.base import reverse
from django.utils import feedgenerator
from django.utils.feedgenerator import rfc2822_date
from django_ical.views import ICalFeed

from . import models


class EventFeed(ICalFeed):
    """
    A simple event calender
    """

    product_id = "-//dukop.dk//Kalender"
    timezone = "UTC"
    file_name = "dukop.ics"

    def items(self):
        return models.EventTime.objects.future()

    def item_link(self, item):
        return item.event.share_link()

    def item_title(self, item):
        return item.event.name

    def item_description(self, item):
        return item.event.short_description

    def item_start_datetime(self, item):
        return item.start.astimezone(pytz.timezone("UTC"))

    def item_end_datetime(self, item):
        return item.end.astimezone(pytz.timezone("UTC"))

    def item_location(self, item):
        location = item.event.venue_name or ""
        if item.event.street:
            location += "\n" + item.event.street
        if item.event.city:
            location += "\n" + item.event.city
        if item.event.zip_code:
            location += " " + item.event.zip_code
        return location


class DukOpEventRssGenerator(feedgenerator.Rss201rev2Feed):
    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        handler.addQuickElement("start_datetime", str(item["start_datetime"]))


class RssFeed(Feed):
    """
    TODO: This feed should specify a Sphere using get_object etc.
    """

    feed_type = DukOpEventRssGenerator

    def item_extra_kwargs(self, item):
        """
        Return an extra keyword arguments dictionary that is used with
        the `add_item` call of the feed generator.
        """
        return {
            "start_datetime": self.item_start_datetime(item),
            "end_datetime": self.item_end_datetime(item),
            "location": self.item_location(item),
        }

    def title(self):
        return "Upcoming 30 events on DukOp"

    def description(self, obj):
        """
        obj: Needs to be a Sphere object
        """
        return "Rss feed of the latest events on DukOp"

    def items(self):
        return models.EventTime.objects.future()[:30]

    def feed_url(self):
        return reverse("calendar:feed_rss")

    def feed_guid(self, obj):
        return 1

    def link(self):
        return reverse("calendar:index")

    # COPYRIGHT NOTICE -- One of the following three is optional. The
    # framework looks for them in this order.

    feed_copyright = "CopyLeft"  # Hard-coded copyright notice.

    ttl = 600  # Hard-coded Time To Live.

    def item_link(self, item):
        return item.event.share_link()

    def item_title(self, item):
        return item.event.name

    def item_location(self, item):
        location = item.event.venue_name or ""
        if item.event.street:
            location += "\n" + item.event.street
        if item.event.city:
            location += "\n" + item.event.city
        if item.event.zip_code:
            location += " " + item.event.zip_code
        return location

    def item_author_name(self, item):
        return item.event.get_display_host()

    def item_description(self, item):
        return item.event.short_description

    def item_start_datetime(self, item):
        return rfc2822_date(item.start.astimezone(pytz.timezone("UTC")))

    def item_end_datetime(self, item):
        return (
            rfc2822_date(item.end.astimezone(pytz.timezone("UTC"))) if item.end else ""
        )

    def item_pubdate(self, item):
        """
        Takes an item, as returned by items(), and returns the item's
        pubdate.
        """
        return item.event.created

    def item_categories(self, item):
        """
        TODO: Once we have categories
        """
        return []
