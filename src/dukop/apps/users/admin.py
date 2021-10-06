from django.contrib import admin

from . import models


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "event_count", "deactivated", "is_restricted")
    list_filter = (
        "is_restricted",
        "deactivated",
    )
    search_fields = ("name",)

    def event_count(self, instance):
        return instance.events.all().count()


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    pass
