from django.db import models
from django.urls.base import reverse
from django.utils.translation import gettext_lazy as _
from markdownfield.models import MarkdownField
from markdownfield.models import RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD


class NewsStory(models.Model):

    headline = models.CharField(max_length=512)
    short_story = models.TextField()

    text = MarkdownField(rendered_field="text_rendered", validator=VALIDATOR_STANDARD)
    text_rendered = RenderedMarkdownField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    url = models.URLField(blank=True, null=True)

    @property
    def url_read_more(self):
        if self.url:
            return self.url
        return reverse("news:story", kwargs={"pk": self.pk})

    def __str__(self):
        return self.headline

    class Meta:
        ordering = ("-created",)
        verbose_name = _("News story")
        verbose_name_plural = _("News stories")
