from django import forms
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext_lazy as _

from . import models


def get_confirm_code(email):
    return default_token_generator(email)[:7]


class EmailLogin(forms.Form):

    email = forms.EmailField(label=_("Email"), required=True)


class TokenLogin(forms.Form):

    def __init__(self, *args, **kwargs):
        self.token_uuid = kwargs.pop("token_uuid")
        super().__init__(*args, **kwargs)

    token_passphrase = forms.CharField(label=_("Token"), required=True)

    def clean_token_passphrase(self):
        token_passphrase = self.cleaned_data.get('token_passphrase')
        try:
            self.user = models.User.objects.token_eligible().get(token_uuid=self.token_uuid, token_passphrase=token_passphrase)
            return token_passphrase
        except models.User.DoesNotExist:
            raise forms.ValidationError("Not correct - did your token expire or did you enter it wrongly?")


class SignupForm(forms.Form):
    """
    This is the form for signing up.. it doesn't contain anything but will
    just create a new empty user object and send an email. If the email already
    exists, it will send a login token.
    """

    email = forms.EmailField(label=_("Email"), required=True)
