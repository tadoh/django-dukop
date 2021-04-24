import pytest
from django.core.management import call_command


@pytest.mark.django_db(transaction=True)
def test_with_client(client):
    response = client.get("/en/")
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_fixtures(client):
    """
    Test event creation by calling our fixture management command
    """
    call_command("calendar_fixtures", local_image=True)
