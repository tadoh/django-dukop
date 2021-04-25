from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from . import models


class AboutView(TemplateView):
    template_name = "news/about.html"


class NewsStoryView(DetailView):
    template_name = "news/story.html"
    model = models.NewsStory
    queryset = models.NewsStory.objects.filter(published=True)

    context_object_name = "story"
