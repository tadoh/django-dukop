from django.contrib import admin

from . import models


@admin.register(models.NewsStory)
class NewsStoryAdmin(admin.ModelAdmin):
    list_display = ("headline", "created", "short_story")
