import pytz
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django_ical.views import ICalFeed
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
            if self.request.user.is_authenticated:
                qs = qs.filter(
                    Q(published=True)
                    | Q(owner_user=self.request.user)
                    | Q(owner_group__members=self.request.user)
                )
            else:
                qs = qs.filter(published=True)
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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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


def set_sphere_session(request, pk):
    get_object_or_404(models.Sphere, pk=pk)
    request.session["dukop_sphere"] = pk

    next_url = request.GET.get("next")
    if not next_url:
        next_url = reverse("calendar:index")
    return redirect(next_url)


class EventFeed(ICalFeed):
    """
    A simple event calender
    """

    product_id = "-//dukop.dk//Kalender"
    timezone = "UTC"
    file_name = "dukop.ics"

    def items(self):
        return models.EventTime.objects.future()

    def item_link(self, item):
        return item.event.share_link()

    def item_title(self, item):
        return item.event.name

    def item_description(self, item):
        return item.event.short_description

    def item_start_datetime(self, item):
        return item.start.astimezone(pytz.timezone("UTC"))

    def item_end_datetime(self, item):
        return item.end.astimezone(pytz.timezone("UTC"))

    def item_location(self, item):
        location = item.event.venue_name or ""
        if item.event.street:
            location += "\n" + item.event.street
        if item.event.city:
            location += "\n" + item.event.city
        if item.event.zip_code:
            location += " " + item.event.zip_code
        return location
