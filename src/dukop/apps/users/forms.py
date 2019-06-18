from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext_lazy as _

from . import models


def get_confirm_code(email):
    return default_token_generator(email)[:7]


class SignupForm(UserCreationForm):

    username = forms.EmailField(label=_("Email"))

    class Meta:
        model = models.User
        fields = ("username",)
