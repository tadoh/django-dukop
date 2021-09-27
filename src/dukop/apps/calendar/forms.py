from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _
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

    host = forms.ModelChoiceField(
        queryset=Group.objects.filter(deactivated=False, is_restricted=False)
        .filter(events__published=True)
        .distinct(),
        required=False,
        label=_("Existing venue"),
        help_text=_(
            "Choose venues from an existing list, otherwise create a new one below"
        ),
    )

    class Meta:
        model = models.Event
        fields = (
            "name",
            "description",
            "host",
            "venue_name",
            "street",
            "zip_code",
            "city",
            "spheres",
        )
        help_texts = {
            "host": _(
                "A group may host an event and be displayed as the author of the event text. You can only choose a host if you have been allowed membership of a group."
            )
        }


class EventTimeForm(forms.ModelForm):

    start = forms.SplitDateTimeField(widget=SplitDateTimeWidget())
    end = forms.SplitDateTimeField(widget=SplitDateTimeWidget(), required=False)

    class Meta:
        model = models.EventTime
        fields = ("start", "end")


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
        return image

    class Meta:
        model = models.EventImage
        fields = ("image", "is_cover")


class EventLinkForm(forms.ModelForm):
    class Meta:
        model = models.EventLink
        fields = ("link",)


class EventRecurrenceForm(forms.ModelForm):

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


EventTimeFormSet = inlineformset_factory(
    models.Event,
    models.EventTime,
    EventTimeForm,
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
