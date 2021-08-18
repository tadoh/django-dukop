from functools import wraps

import pytest
from django.core.cache import cache
from django.urls.base import reverse

from .fixtures_users import single_user  # noqa


def clear_cache(test_func):
    @wraps(test_func)
    def inner(*args, **kwargs):
        cache.clear()
        return test_func(*args, **kwargs)

    return inner


def assert_fail_on_repeat(client, url, no_times=5):
    for __ in range(no_times):
        response = client.post(url)
        assert response.status_code == 200
    response = client.post(url)
    assert response.status_code == 429


@clear_cache
@pytest.mark.django_db(transaction=True)
def test_login_page_ratelimit(client):
    assert_fail_on_repeat(client, reverse("users:login"), 5)


@clear_cache
@pytest.mark.django_db(transaction=True)
def test_signup_page_ratelimit(client):
    assert_fail_on_repeat(client, reverse("users:login"), 5)


@clear_cache
@pytest.mark.django_db(transaction=True)
def test_token_page_ratelimit(client, single_user):  # noqa
    single_user.set_token()
    assert_fail_on_repeat(
        client,
        reverse("users:login_token", kwargs={"token": single_user.token_uuid}),
        5,
    )
