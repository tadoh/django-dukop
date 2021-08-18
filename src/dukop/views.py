from django.http.response import HttpResponse
from django.http.response import HttpResponseForbidden
from ratelimit.exceptions import Ratelimited


def handler403(request, exception=None):
    if isinstance(exception, Ratelimited):
        return HttpResponse("Sorry you are blocked", status=429)
    return HttpResponseForbidden("Forbidden")
