import pytest
from dukop.apps.users import models


@pytest.fixture
def single_user(db):
    user = models.User.objects.create(email="test@example.org")
    return user
