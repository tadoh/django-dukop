import random

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext_lazy as _

from . import models


def get_confirm_code(email):
    return default_token_generator(email)[:7]


class EmailLogin(forms.Form):

    email = forms.EmailField(label=_("Email"), required=True, widget=forms.EmailInput(attrs={'autofocus': True}))


class PasswordLogin(AuthenticationForm):
    pass


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


bot_questions_answers = [
    (_("Are you a 'bot' or a 'human'?"), _("human")),
    (_("What do you do when you are not awake? Starts with S, ends with P."), _("sleep")),
    (_("Toilets. We all use them. After which we... [fl*sh]. Just write that word here."), _("flush")),
]


class SignupForm(forms.Form):
    """
    This is the form for signing up.. it doesn't contain anything but will
    just create a new empty user object and send an email. If the email already
    exists, it will send a login token.
    """

    bot_q = forms.IntegerField(widget=forms.HiddenInput(), required=True)

    email = forms.EmailField(label=_("Email"), required=True)

    no_bots = forms.CharField(label=_("Are you a bot?"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            question_choice = int(self.data.get('bot_q', False)) or random.randint(0, len(bot_questions_answers) - 1)
        except (IndexError, ValueError):
            question_choice = random.randint(0, len(bot_questions_answers) - 1)
        question = bot_questions_answers[question_choice]
        self.fields['no_bots'].label = question[0]
        self.answer = question[1]
        self.fields['bot_q'].initial = question_choice

    def clean_no_bots(self):
        correct_answer = self.cleaned_data.get('bot_q')
        if not correct_answer:
            raise forms.ValidationError("Nah, you seem like a bot")
        if self.cleaned_data['no_bots'].lower() == bot_questions_answers[correct_answer][1].lower():
            return self.cleaned_data['no_bots'].lower()
        raise forms.ValidationError("Nah, you seem like a bot")
