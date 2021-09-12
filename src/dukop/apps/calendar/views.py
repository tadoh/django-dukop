from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls.base import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from ratelimit.decorators import ratelimit

from . import forms
from . import models


def index(request):
    return render(request, "calendar/index.html")


class FeedInstructionView(TemplateView):
    template_name = "calendar/feeds/instructions.html"

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c["spheres"] = models.Sphere.get_all_cached()
        return c


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
        self.recurrences_form = forms.EventRecurrenceFormSet(prefix="recurrences")
        return self.render_to_response(self.get_context_data())

    @method_decorator(ratelimit(key="ip", rate="10/d", method="POST"))
    @method_decorator(ratelimit(key="ip", rate="5/h", method="POST"))
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
        self.recurrences_form = forms.EventRecurrenceFormSet(
            data=request.POST, prefix="recurrences"
        )
        form = self.get_form()
        if (
            form.is_valid()
            and self.images_form.is_valid()
            and self.times_form.is_valid()
            and self.links_form.is_valid()
            and self.recurrences_form.is_valid()
        ):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    @transaction.atomic()
    def form_valid(self, form):  # noqa: max-complexity=13
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

        for form in self.recurrences_form:
            if form.is_valid() and form.has_changed():
                if form.cleaned_data.get("DELETE") and form.instance.pk:
                    pass
                else:
                    recurrence = form.save(commit=False)
                    recurrence.event = event
                    recurrence.event_time_anchor = event.times.all().first()
                    recurrence.save()
                    recurrence.sync()

        return redirect("calendar:event_create_success", pk=event.pk)

    def form_invalid(self, form):
        self.forms_had_errors = True
        return CreateView.form_invalid(self, form)

    def get_context_data(self, **kwargs):
        c = CreateView.get_context_data(self, **kwargs)
        c["times"] = self.times_form
        c["images"] = self.images_form
        c["links"] = self.links_form
        c["recurrences"] = self.recurrences_form
        c["forms_had_errors"] = getattr(self, "forms_had_errors", False)
        return c

    def get_initial(self):
        initial = super().initial
        initial["spheres"] = models.Sphere.objects.filter(id=self.request.sphere.id)
        return initial


class EventListView(ListView):
    """
    This lists all Event objects -- BUT! Notice that the listing is happening
    via the EventTime relation. We are only ever interested in listing events
    from their occurrence in time, past present or future. The essential feature
    of the list is to be chronological.
    """

    template_name = "calendar/event/list.html"
    model = models.EventTime
    context_object_name = "event_times"
    max_days_lookback = 30

    def dispatch(self, request, *args, **kwargs):
        sphere_id = kwargs.get("sphere_id", None)
        self.sphere = None
        if sphere_id:
            self.sphere = get_object_or_404(models.Sphere, pk=sphere_id)

        self.pivot_date = kwargs.get("pivot_date", None)
        if not self.pivot_date:
            self.pivot_date = timezone.now().date()

        self.pivot_date_end = self.pivot_date + timedelta(days=7)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = DetailView.get_queryset(self)

        if not self.request.user or not self.request.user.is_staff:
            q_visible_to_all = Q(event__published=True) & Q(
                start__gte=timezone.now() - timedelta(days=self.max_days_lookback)
            )
            if self.request.user.is_authenticated:
                qs = qs.filter(
                    q_visible_to_all
                    | Q(event__owner_user=self.request.user)
                    | Q(event__owner_group__members=self.request.user)
                )
            else:
                qs = qs.filter(q_visible_to_all)

        qs = qs.filter(start__gte=self.pivot_date, start__lte=self.pivot_date_end)

        if self.sphere:
            qs = qs.filter(event__spheres=self.sphere)

        return qs

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c["pivot_date"] = self.pivot_date
        c["pivot_date_end"] = self.pivot_date_end
        c["pivot_date_next"] = self.pivot_date_end
        c["pivot_date_previous"] = self.pivot_date - timedelta(days=7)
        c["sphere"] = self.sphere
        return c


def set_sphere_session(request, pk):
    get_object_or_404(models.Sphere, pk=pk)
    request.session["dukop_sphere"] = pk

    next_url = request.GET.get("next")
    if not next_url:
        next_url = reverse("calendar:index")
    return redirect(next_url)
