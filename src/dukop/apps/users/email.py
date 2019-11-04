from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail.message import EmailMessage
from django.template import loader
from django.utils.translation import ugettext_lazy as _


class BaseEmail(EmailMessage):

    template = "users/mail/base.txt"
    default_subject = "SET SUBJECT HERE"

    def __init__(self, request, *args, **kwargs):
        self.context = kwargs.pop('context', {})
        self.user = kwargs.pop('user', None)
        if self.user:
            kwargs['to'] = [self.user.email]
            self.context['user'] = self.user
            self.context['recipient_name'] = self.user.get_display_name()

        kwargs.setdefault('subject', self.default_subject)

        super().__init__(*args, **kwargs)
        self.request = request
        self.body = self.get_body()

    def get_context_data(self):
        c = self.context
        site = get_current_site(self.request)
        c['request'] = self.request
        c['domain'] = site.domain
        c['site_name'] = site.name
        c['protocol'] = 'https' if self.request and self.request.is_secure() else 'http'
        return c

    def get_body(self):
        return loader.render_to_string(self.template, self.get_context_data())

    def send_with_feedback(self, success_msg=None):
        if not success_msg:
            success_msg = _("Email successfully sent to {}".format(", ".join(self.to)))
        try:
            self.send(fail_silently=False)
            messages.success(
                self.request,
                success_msg
            )
        except RuntimeError:
            messages.error(
                self.request,
                _("Not sent, something wrong with the mail server.")
            )


class UserConfirm(BaseEmail):

    template = "users/mail/new_account_with_password.txt"
    default_subject = _("Your new account for dukop")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UserToken(BaseEmail):

    template = "users/mail/token_login.txt"
    default_subject = _("")

    def __init__(self, *args, **kwargs):
        self.next = kwargs.pop("next", None)
        super().__init__(*args, **kwargs)

    def get_context_data(self):
        c = super().get_context_data()
        c['next'] = self.next
        return c
