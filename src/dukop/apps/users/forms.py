from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext_lazy as _

from . import models


def get_confirm_code(email):
    return default_token_generator(email)[:7]


class SignupForm(UserCreationForm):

    username = forms.EmailField(label=_("Email"))

    def clean_username(self):
        username = self.cleaned_data.get("username", None)
        if username and models.User.objects.filter(email__iexact=username).exists():
            raise forms.ValidationError("Choose another email.")
        return username

    class Meta:
        model = models.User
        fields = ("username",)
