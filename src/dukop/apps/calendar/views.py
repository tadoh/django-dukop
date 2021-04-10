from django.shortcuts import render
from django.views.generic.edit import CreateView
from ratelimit.decorators import ratelimit

from . import forms
from . import models


def index(request):
    return render(request, "calendar/index.html")


class EventCreate(CreateView):

    template_name = "calendar/event/create.html"
    model = models.Event
    form_class = forms.EventForm

    def get(self, request, *args, **kwargs):
        """Handle GET requests: instantiate a blank version of the form."""
        self.object = None
        self.images_form = forms.EventImageFormSet(prefix="images")
        self.times_form = forms.EventTimeFormSet(prefix="times")
        self.links_form = forms.EventLinkFormSet(prefix="links")
        return self.render_to_response(self.get_context_data())

    @ratelimit(key="ip", rate="5/h", method="POST")
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = None
        self.images_form = forms.EventImageFormSet(data=request.POST, prefix="images")
        self.times_form = forms.EventTimeFormSet(data=request.POST, prefix="times")
        self.links_form = forms.EventLinkFormSet(data=request.POST, prefix="links")
        form = self.get_form()
        if (
            form.is_valid()
            and self.images_form.is_valid()
            and self.times_form.is_valid()
            and self.links_form.is_valid()
        ):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return CreateView.form_valid(self, form)

    def form_invalid(self, form):
        self.forms_had_errors = True
        return CreateView.form_invalid(self, form)

    def get_context_data(self, **kwargs):
        c = CreateView.get_context_data(self, **kwargs)
        c["times"] = self.times_form
        c["images"] = self.images_form
        c["links"] = self.links_form
        c["forms_had_errors"] = getattr(self, "forms_had_errors", False)
        return c
