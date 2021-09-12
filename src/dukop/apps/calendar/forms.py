from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import gettext_lazy as _

from . import models
from .widgets import SplitDateTimeWidget


class EventForm(forms.ModelForm):

    spheres = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=models.Sphere.objects.all(),
        label=_("Relevance"),
        help_text=_("Select which versions of the calendar this is relevant for."),
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
        required=False,
    )

    end = forms.SplitDateTimeField(widget=SplitDateTimeWidget(), required=False)

    class Meta:
        model = models.EventRecurrence
        fields = ("end",)


EventTimeFormSet = formset_factory(
    EventTimeForm,
    extra=5,
    max_num=5,
    validate_min=1,
)
EventImageFormSet = formset_factory(EventImageForm, extra=5, max_num=5)
EventLinkFormSet = formset_factory(EventLinkForm, extra=5, max_num=5)
EventRecurrenceFormSet = formset_factory(EventRecurrenceForm, extra=2, max_num=2)
