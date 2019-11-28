from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import SuccessURLAllowedHostsMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import resolve_url
from django.urls.base import reverse_lazy
from django.utils.http import is_safe_url
from django.utils.translation import gettext as _
from django.views.generic.base import RedirectView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from ratelimit.decorators import ratelimit

from . import email
from . import forms
from . import models


class PasswordResetView(auth_views.PasswordResetView):
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy('users:password_reset_complete')


class PasswordChangeView(auth_views.PasswordChangeView):
    success_url = reverse_lazy('users:password_change_done')


class LoginView(FormView, SuccessURLAllowedHostsMixin):

    template_name = "users/login.html"
    form_class = forms.EmailLogin
    redirect_field_name = 'next'

    @ratelimit(key='ip', rate='5/h', method='POST')
    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        c = FormView.get_context_data(self, **kwargs)
        c['password_form'] = forms.PasswordLogin()
        return c

    def form_valid(self, form):
        try:
            user = models.User.objects.get(email=form.cleaned_data["email"])
            user.set_token()
            mail = email.UserToken(self.request, user=user, next=self.request.GET.get(self.redirect_field_name, ''))
            mail.send_with_feedback(success_msg=_("Check your inbox"))
        except models.User.DoesNotExist:
            pass
        self.request.session['email_token'] = form.cleaned_data["email"]
        return redirect("users:login_token_sent")


class LoginPasswordView(FormView, SuccessURLAllowedHostsMixin):

    template_name = "users/login_password.html"
    form_class = forms.PasswordLogin
    redirect_field_name = 'next'

    @ratelimit(key='ip', rate='5/h', method='POST')
    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.user_cache, backend=None)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''


class LoginTokenSentView(TemplateView):

    template_name = "users/login_token_sent.html"

    def get_context_data(self, **kwargs):
        c = TemplateView.get_context_data(self, **kwargs)
        c['email_token'] = self.request.session['email_token']
        return c


class LoginTokenView(FormView, SuccessURLAllowedHostsMixin):

    template_name = "users/login_token.html"
    form_class = forms.TokenLogin
    redirect_field_name = 'next'

    @ratelimit(key='ip', rate='5/h', method='POST')
    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = FormView.get_form_kwargs(self)
        kwargs["token_uuid"] = self.kwargs["token"]
        return kwargs

    def form_valid(self, form):
        # Find a suitable backend.
        login(self.request, form.user, backend=settings.AUTHENTICATION_BACKENDS[0])
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''


class SignupView(FormView):

    template_name = "users/signup.html"
    form_class = forms.SignupForm

    @ratelimit(key='ip', rate='5/h', method='POST')
    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)

    def form_valid(self, form):

        try:
            user = models.User.objects.get(email=form.cleaned_data["email"])
            user.set_token()
            mail = email.UserToken(self.request, user=user)
            mail.send_with_feedback(success_msg=_("Check your inbox"))
        except models.User.DoesNotExist:
            user = models.User.objects.create_user(email=form.cleaned_data["email"])
            user.is_active = True  # The user is active by default
            user.save()
            user.set_token()
            mail = email.UserConfirm(self.request, user=user)
            mail.send_with_feedback(success_msg=_("Check your inbox"))

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
