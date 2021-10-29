from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from dukop.apps.calendar.utils import get_now
from dukop.apps.users.models import Group

from . import models
from .widgets import SplitDateTimeWidget


class EventForm(forms.ModelForm):

    spheres = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=models.Sphere.objects.all(),
        label=_("Relevance"),
        help_text=_("Select which versions of the calendar this is relevant for."),
    )

    location = forms.ModelChoiceField(
        queryset=Group.objects.filter(deactivated=False, is_restricted=False)
        .filter(events__published=True)
        .distinct(),
        required=False,
        label=_("Location"),
        help_text=_("Choose an existing location or create a new one"),
    )

    class Meta:
        model = models.Event
        fields = (
            "name",
            "description",
            "location",
            "venue_name",
            "street",
            "zip_code",
            "city",
            "spheres",
        )


class CreateEventForm(EventForm):

    host = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        required=False,
        label=_("Host group"),
        help_text=_("Choose one of your existing groups or create a new one"),
    )

    new_host = forms.CharField(
        label=_("New group"),
        help_text=_(
            "Name of the new group, for instance 'Marxist Book Reading Circle'"
        ),
    )

    class Meta(EventForm.Meta):
        fields = (
            "name",
            "description",
            "host",
            "new_host",
            "location",
            "venue_name",
            "street",
            "zip_code",
            "city",
            "spheres",
        )
        help_texts = {
            "host": _(
                "A group may host an event and be displayed as the author of the event text. You can only choose an existing group if you have been allowed membership of that group."
            )
        }


class EventTimeForm(forms.ModelForm):

    start = forms.SplitDateTimeField(widget=SplitDateTimeWidget())
    end = forms.SplitDateTimeField(widget=SplitDateTimeWidget(), required=False)

    def clean_start(self):
        start = self.cleaned_data["start"]
        if self.has_changed() and start < get_now():
            raise forms.ValidationError("Start cannot be in the past.")
        return start

    class Meta:
        model = models.EventTime
        fields = ["start", "end"]


class EventTimeUpdateForm(EventTimeForm):
    class Meta(EventTimeForm.Meta):
        fields = EventTimeForm.Meta.fields + ["is_cancelled"]


class EventImageForm(forms.ModelForm):

    is_cover = forms.BooleanField(
        required=False,
        label=_("Cover image"),
        help_text=_("If you have several images, use this one as the cover"),
    )

    def save(self, commit=True):
        # A very naive implementation of priority, just sets '0' on the
        # cover image
        image = forms.ModelForm.save(self, commit=False)
        if self.cleaned_data.get("is_cover", False):
            image.priority = 0
        else:
            image.priority = 1
        image.save()
        return image

    class Meta:
        model = models.EventImage
        fields = ("image", "is_cover")


class EventLinkForm(forms.ModelForm):
    class Meta:
        model = models.EventLink
        fields = ("link",)


class EventRecurrenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields["interval_type"].initial = self.instance.recurrence_type

    interval_type = forms.ChoiceField(
        choices=[("", "----")] + models.EventRecurrence.RECURRENCE_TYPES,
        required=True,
    )

    end = forms.SplitDateTimeField(widget=SplitDateTimeWidget(), required=False)

    def save(self, commit=True):
        recurrence = super().save(commit=commit)
        for field_name, __ in models.EventRecurrence.RECURRENCE_TYPES:
            setattr(recurrence, field_name, False)
        setattr(recurrence, self.cleaned_data["interval_type"], True)
        return recurrence

    class Meta:
        model = models.EventRecurrence
        fields = ("end",)


class EventRecurrenceTimesForm(forms.ModelForm):

    start = forms.SplitDateTimeField(widget=SplitDateTimeWidget())
    end = forms.SplitDateTimeField(widget=SplitDateTimeWidget(), required=False)

    class Meta:
        model = models.EventTime
        fields = ["start", "end", "is_cancelled"]


EventTimeFormSet = inlineformset_factory(
    models.Event,
    models.EventTime,
    EventTimeForm,
    extra=5,
    max_num=5,
    min_num=1,
    validate_min=True,
)

EventTimeUpdateFormSet = inlineformset_factory(
    models.Event,
    models.EventTime,
    EventTimeUpdateForm,
    extra=5,
    max_num=5,
    min_num=1,
    validate_min=True,
)

EventImageFormSet = inlineformset_factory(
    models.Event, models.EventImage, EventImageForm, extra=5, max_num=5
)
EventLinkFormSet = inlineformset_factory(
    models.Event, models.EventLink, EventLinkForm, extra=5, max_num=5
)
EventRecurrenceFormSet = inlineformset_factory(
    models.Event, models.EventRecurrence, EventRecurrenceForm, extra=2, max_num=2
)
EventRecurrenceTimesFormSet = inlineformset_factory(
    models.Event,
    models.EventTime,
    EventRecurrenceTimesForm,
    extra=0,
    can_delete=False,
)
