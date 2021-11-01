import pytest
from dukop.apps.users import models

SINGLE_USER_PASSWORD = "lalalalalalalala"


@pytest.fixture
def single_user(db):
    user = models.User.objects.create(email="test@example.org")
    user.set_password(SINGLE_USER_PASSWORD)
    user.save()
    return user
