from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import gettext_lazy as _

from . import models
from .widgets import SplitDateTimeWidget


class EventForm(forms.ModelForm):

    class Meta:
        model = models.Event
        fields = ('name', 'description', 'host', 'venue_name', 'street', 'zip_code', 'city')
        help_texts = {
            'host': _("A group may host an event and be displayed as the author of the event text. You can only choose a host if you have been allowed membership of a group.")
        }


class EventTimeForm(forms.ModelForm):

    start = forms.DateTimeField(widget=SplitDateTimeWidget())
    end = forms.DateTimeField(widget=SplitDateTimeWidget())

    class Meta:
        model = models.EventTime
        fields = ('start', 'end')


class EventImageForm(forms.ModelForm):

    is_cover = forms.BooleanField()

    def save(self, commit=True):
        # A very naive implementation of priority, just sets '0' on the
        # cover image
        image = forms.ModelForm.save(self, commit=False)
        if self.cleaned_data['is_cover']:
            image.priority = 0
        else:
            image.priority = 1
        return image

    class Meta:
        model = models.EventImage
        fields = ('image',)


class EventLinkForm(forms.ModelForm):

    class Meta:
        model = models.EventLink
        fields = ('link',)


EventTimeFormSet = formset_factory(EventTimeForm, extra=5, max_num=5)
EventImageFormSet = formset_factory(EventImageForm, extra=5, max_num=5)
EventLinkFormSet = formset_factory(EventLinkForm, extra=5, max_num=5)
