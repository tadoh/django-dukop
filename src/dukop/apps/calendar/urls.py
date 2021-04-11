from django.urls import path

from . import views


app_name = "calendar"

urlpatterns = [
    path("", views.index),
    path(
        "event/<slug:slug>/<int:pk>/",
        views.EventDetailView.as_view(),
        name="event_detail",
    ),
    path("event/<int:pk>/", views.EventDetailView.as_view(), name="event_detail"),
    path("event/create", views.EventCreate.as_view(), name="event_create"),
]
