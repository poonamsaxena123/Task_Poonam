from django.urls import path

from .views import (EventListCreateView, LoginView, RegisterView,
                    EventRetrieveUpdateDestroyView, EventParticipantCreate
                    , EventParticipantsList, SendInvitationView, ListInvitationsView ,RespondInvitationView )

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("create-events/", EventListCreateView.as_view(), name="event-create"),
    path("events/list/", EventListCreateView.as_view(), name="event-list"),
    path(
        "events/<int:id>/",
        EventRetrieveUpdateDestroyView.as_view(),
        name="event-detail",
    ),
    path('events/<int:event_id>/register/', EventParticipantCreate.as_view(), name='event-register'),
    
    path('events/<int:event_id>/participants/', EventParticipantsList.as_view(), name='event-participants'),
    path('events/<int:event_id>/invite/', SendInvitationView.as_view(), name='event-invitation'),
    path('list-invitations/', ListInvitationsView.as_view(), name='invitations'),
    path("check-status/<int:event_id>/",RespondInvitationView.as_view(),name='invitation-status'),

]
