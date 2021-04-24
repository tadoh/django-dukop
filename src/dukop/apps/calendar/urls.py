from django.urls import path

from . import views


app_name = "calendar"

urlpatterns = [
    path("", views.index),
    path("event/<int:pk>/", views.EventDetailView.as_view(), name="event_detail"),
    path("event/create", views.EventCreate.as_view(), name="event_create"),
    path(
        "event/create/<int:pk>/",
        views.EventCreateSuccess.as_view(),
        name="event_create_success",
    ),
    path(
        "event/<slug:slug>/<int:pk>/",
        views.EventDetailView.as_view(),
        name="event_detail",
    ),
]
