import random
from datetime import timedelta

import pytest
from django.urls.base import reverse
from django.utils import timezone
from dukop.apps.calendar import forms
from dukop.apps.calendar.models import Event
from dukop.apps.calendar.models import Sphere

from .fixtures_users import single_user  # noqa
from .fixtures_users import SINGLE_USER_PASSWORD


@pytest.mark.django_db(transaction=True)
def test_create_event(client, single_user):  # noqa
    client.login(username=single_user.email, password=SINGLE_USER_PASSWORD)
    response = client.get(reverse("calendar:event_create"))
    assert response.status_code == 200

    # data will receive all the forms field names
    # key will be the field name (as "formx-fieldname"), value will be the string representation.
    data = {}

    # global information, some additional fields may go there
    data["csrf_token"] = response.context["csrf_token"]

    # management form information, needed because of the formset
    for form_name in ["times", "recurrences", "images", "links"]:
        management_form = response.context[form_name].management_form
        for i in "TOTAL_FORMS", "INITIAL_FORMS", "MIN_NUM_FORMS", "MAX_NUM_FORMS":
            data["%s-%s" % (management_form.prefix, i)] = management_form[i].value()

        for i in range(response.context[form_name].total_form_count()):
            # get form index 'i'
            current_form = response.context[form_name].forms[i]

            # retrieve all the fields
            for field_name in current_form.fields:
                value = current_form[field_name].value()
                data["%s-%s" % (current_form.prefix, field_name)] = (
                    value if value is not None else ""
                )

    first_times_form = response.context["times"].forms[0]
    start_datetime = timezone.now() + timedelta(days=1)
    data["%s-%s_0" % (first_times_form.prefix, "start")] = start_datetime.date()
    data["%s-%s_1" % (first_times_form.prefix, "start")] = start_datetime.strftime(
        "%H:%M"
    )

    event_name = f"Test event {random.randint(10000, 99999)}"

    data["name"] = event_name
    data["spheres"] = Sphere.objects.all()[0].pk
    data["host_choice"] = forms.CreateEventForm.HOST_NEW
    data["location_choice"] = forms.EventForm.LOCATION_NEW

    data["new_host"] = "Test group {random.randint(10000, 99999)}"

    print(data)

    response = client.post(reverse("calendar:event_create"), data=data)
    assert response.status_code == 302

    assert Event.objects.all().latest("id").name == event_name
