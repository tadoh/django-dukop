from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from ratelimit.decorators import ratelimit

from . import forms
from . import models


def index(request):
    return render(request, "calendar/index.html")


class EventDetailView(DetailView):

    template_name = "calendar/event/detail.html"
    model = models.Event
    context_object_name = "event"

    def get_queryset(self):
        qs = DetailView.get_queryset(self)

        if not self.request.user or not self.request.user.is_staff:
            qs = qs.filter(
                Q(published=True)
                | Q(owner_user=self.request.user)
                | Q(owner_group__members=self.request.user)
            )
        return qs


class EventCreateSuccess(EventDetailView):
    """
    Same as viewing an event - but with a different template
    """

    template_name = "calendar/event/create_success.html"


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
        self.images_form = forms.EventImageFormSet(
            data=request.POST, files=request.FILES, prefix="images"
        )
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

    @transaction.atomic()
    def form_valid(self, form):
        self.object = form.save()
        event = self.object

        for form in self.images_form:
            if form.is_valid() and form.cleaned_data.get("image"):
                if form.cleaned_data.get("DELETE") and form.instance.pk:
                    pass
                else:
                    image = form.save(commit=False)
                    image.event = event
                    image.save()

        for form in self.times_form:
            if form.is_valid() and form.has_changed():
                if form.cleaned_data.get("DELETE") and form.instance.pk:
                    pass
                else:
                    times = form.save(commit=False)
                    times.event = event
                    times.save()

        for form in self.links_form:
            if form.is_valid() and form.has_changed():
                if form.cleaned_data.get("DELETE") and form.instance.pk:
                    pass
                else:
                    link = form.save(commit=False)
                    link.event = event
                    link.save()

        return redirect("calendar:event_create_success", pk=event.pk)

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
