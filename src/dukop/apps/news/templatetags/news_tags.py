from django import template

from .. import models

register = template.Library()


@register.simple_tag
def get_short_news(
    max_count=3,
):

    return (
        models.NewsStory.objects.filter(published=True)
        .exclude(short_story="")
        .order_by("-created")[: int(max_count)]
    )
