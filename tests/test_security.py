import pytest
from django.urls.base import reverse


@pytest.mark.django_db(transaction=True)
def test_login_page_ratelimit(client):
    response = client.post(reverse("users:login"))
    assert response.status_code == 200
    response = client.post(reverse("users:login"))
    assert response.status_code == 200
    response = client.post(reverse("users:login"))
    assert response.status_code == 200
    response = client.post(reverse("users:login"))
    assert response.status_code == 200
    response = client.post(reverse("users:login"))
    assert response.status_code == 200
    response = client.post(reverse("users:login"))
    assert response.status_code == 429
