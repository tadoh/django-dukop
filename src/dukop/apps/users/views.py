from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls.base import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.base import RedirectView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from . import email
from . import forms


class PasswordResetView(auth_views.PasswordResetView):
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy('users:password_reset_complete')


class PasswordChangeView(auth_views.PasswordChangeView):
    success_url = reverse_lazy('users:password_change_done')


class SignupView(FormView):

    template_name = "users/signup.html"
    form_class = forms.SignupForm

    def form_valid(self, form):

        user = form.save(commit=False)
        user.is_active = False
        user.set_password(form.cleaned_data['password1'])
        user.save()

        mail = email.UserConfirm(user=user)
        mail.send_with_feedback(success_msg=_("An email was sent with a confirmation link"))

        self.request.session["user_confirm_pending_id"] = user.id

        return redirect("users:signup_confirm")


class SignupConfirmView(TemplateView):

    template_name = "users/signup_confirm.html"


class SignupConfirmRedirectView(RedirectView):

    def get_redirect_url(self):

        uuid = self.kwargs['uuid']

        if self.kwargs["token"] == forms.get_confirm_code(uuid):
            redirect("users:confirmed")  # TODO

        redirect("users:confirm_nope")  # TODO
