from django.urls import path

from .views import (EventListCreateView, LoginView, RegisterView,
                    EventRetrieveUpdateDestroyView)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("events/", EventListCreateView.as_view(), name="event-create"),
    path("events/list/", EventListCreateView.as_view(), name="event-list"),
    path(
        "events/<int:id>/",
        EventRetrieveUpdateDestroyView.as_view(),
        name="event-detail",
    ),
]
