from django.http.response import HttpResponse
from django.http.response import HttpResponseForbidden
from django.shortcuts import render
from ratelimit.exceptions import Ratelimited


def handler403(request, exception=None):
    if isinstance(exception, Ratelimited):
        return HttpResponse("Sorry you are blocked", status=429)
    return HttpResponseForbidden("Forbidden")


def handler404(request, exception):
    return render(request, "404.html", {}, status=404)


def handler500(request, exception=None):
    return render(request, "500.html", {}, status=500)
