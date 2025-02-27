from datetime import timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APITestCase

from events.models import Event, EventParticipant, Feedback, Invitation


class RegisterViewTestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.valid_data = {
            "username": "myuser",
            "email": "myuser@example.com",
            "password": "Test@1234",
        }
        self.invalid_data = {
            "username": "",
            "email": "invalidemail",
            "password": "123",
        }

    def test_successful_valid_data(self):
        response = self.client.post(
            self.register_url, self.valid_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data, {"message": "User registered successfully"}
        )
        self.assertTrue(User.objects.filter(username="myuser").exists())

    def test_invalid_data(self):
        response = self.client.post(
            self.register_url, self.invalid_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)


class LoginViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.login_url = "/api/login/"

    def test_login_successful(self):
        response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "testpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

    def test_login_invalid_data(self):
        response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "Invalid username or password"
        )

    def test_login_missing_username(self):
        response = self.client.post(
            self.login_url, {"password": "testpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "Username and password is required"
        )

    def test_login_missing_password(self):
        response = self.client.post(self.login_url, {"username": "testuser"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "Username and password is required"
        )

    def test_login_missing_credentials(self):
        response = self.client.post(self.login_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "Username and password is required"
        )


class EventListCreateViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin", password="password123"
        )
        self.client.force_authenticate(user=self.user)
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(),
            location="INDORE",
            host=self.user,
            max_participants=50,
        )

        self.event_list_url = reverse("event-list")

    def test_get_events_successful(self):
        response = self.client.get(self.event_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_event_successful(self):
        event_data = {
            "title": "New Event",
            "description": "New Event Description",
            "start_time": "2025-03-10",
            "end_time": "2025-03-11",
            "location": "BHOPAL",
            "host": self.user.id,
            "max_participants": 100,
        }
        response = self.client.post(
            self.event_list_url, data=event_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EventUpdateDestroyTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.event = Event.objects.create(
            id=1,
            title="Test Event",
            description="Test Event Description",
            start_time=timezone.now(),
            host=self.user,
            end_time=timezone.now() + timedelta(),
            location="Test Location",
            max_participants=50,
        )

        self.url = reverse("event-detail", kwargs={"id": self.event.id})
        print(self.url)

    def test_unauthenticated_user_cannot_access_event(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_event(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_update_event(self):
        self.client.force_authenticate(user=self.user)
        updated_data = {"title": "New Update Event"}
        response = self.client.patch(self.url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_event(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())


class EventParticipantRegisterTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.event = Event.objects.create(
            id=1,
            title="Test Event",
            description="Test Event Description",
            start_time=timezone.now(),
            host=self.user,
            end_time=timezone.now() + timedelta(),
            location="Test Location",
            max_participants=50,
        )

        self.url = reverse(
            "event-register", kwargs={"event_id": self.event.id}
        )

    def test_successful_registration(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EventParticipant.objects.count(), 1)

    def test_event_not_found(self):
        self.client.force_authenticate(user=self.user)
        invalid_url = reverse("event-register", kwargs={"event_id": 999})
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_already_registered(self):
        self.client.force_authenticate(user=self.user)
        EventParticipant.objects.create(event=self.event, user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "User already registered for this event"
        )

    def test_authentication_required(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EventParticipantsListTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.host = User.objects.create_user(
            username="hostuser", password="hostpassword"
        )

        self.event = Event.objects.create(
            id=1,
            title="Test Event",
            description="Test Description",
            max_participants=5,
            host=self.host,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2),
        )

        self.participant1 = EventParticipant.objects.create(
            event=self.event, user=self.user
        )

        self.url = reverse(
            "event-participants", kwargs={"event_id": self.event.id}
        )

    def test_get_event_participants_success(self):
        self.client.force_authenticate(user=self.host)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("participants", response.data)
        self.assertEqual(len(response.data["participants"]), 1)

    def test_unauthenticated_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SendInvitationTestCase(APITestCase):

    def setUp(self):
        self.host = User.objects.create_user(
            username="host", password="password"
        )
        self.invitee = User.objects.create_user(
            username="invitee", password="password"
        )
        self.other_user = User.objects.create_user(
            username="other_user", password="password"
        )
        self.event = Event.objects.create(
            title="Test Event",
            host=self.host,
            description="Test Description",
            max_participants=5,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2),
        )
        self.url = reverse(
            "event-invitation", kwargs={"event_id": self.event.id}
        )

    def test_send_invitation_success(self):
        self.client.force_authenticate(user=self.host)
        response = self.client.post(
            self.url, {"invitee": self.invitee.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Invitation.objects.count(), 1)

    def test_send_invitation_event_not_found(self):
        self.client.force_authenticate(user=self.host)
        url = reverse("event-invitation", kwargs={"event_id": 102})
        response = self.client.post(
            url, {"invitee": self.invitee.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_send_invitation_unauthorized(self):
        response = self.client.post(
            self.url, {"invitee": self.invitee.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_send_invitation_missing_invitee(self):
        self.client.force_authenticate(user=self.host)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_invitation_duplicate(self):
        self.client.force_authenticate(user=self.host)
        Invitation.objects.create(
            event=self.event,
            inviter=self.host,
            invitee=self.invitee,
            status="PENDING",
        )
        response = self.client.post(
            self.url, {"invitee": self.invitee.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Invitation.objects.count(), 1)


class RespondInvitationTestCase(APITestCase):

    def setUp(self):
        self.invitee = User.objects.create_user(
            username="invitee", password="password"
        )
        self.host = User.objects.create_user(
            username="host", password="password"
        )
        self.event = Event.objects.create(
            title="Test Event",
            host=self.host,
            description="Test Description",
            max_participants=5,
            start_time=now(),
            end_time=now() + timedelta(hours=2),
        )
        self.invitation = Invitation.objects.create(
            event=self.event,
            inviter=self.host,
            invitee=self.invitee,
            status="PENDING",
        )
        self.url = reverse(
            "invitation-status", kwargs={"event_id": self.event.id}
        )

    def test_respond_invitation_success(self):
        self.client.force_authenticate(user=self.invitee)
        response = self.client.patch(
            self.url, {"status": "ACCEPTED"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.invitation.status, "ACCEPTED")

    def test_invitation_not_found(self):
        self.client.force_authenticate(user=self.invitee)
        url = reverse("invitation-status", kwargs={"event_id": 20})
        response = self.client.patch(
            url, {"status": "ACCEPTED"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_respond_invitation_invalid_status(self):
        self.client.force_authenticate(user=self.invitee)
        response = self.client.patch(
            self.url, {"status": "INVALID"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_respond_invitation_unauthenticated(self):
        response = self.client.patch(
            self.url, {"status": "ACCEPTED"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_respond_invitation_not_invitee(self):
        self.client.force_authenticate(user=self.host)
        response = self.client.patch(
            self.url, {"status": "ACCEPTED"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FeedbackViewTestCase(APITestCase):
    def setUp(self):

        self.host = User.objects.create_user(
            username="host", password="password"
        )
        self.participant = User.objects.create_user(
            username="participant", password="password"
        )
        self.non_participant = User.objects.create_user(
            username="non_participant", password="password"
        )

        self.event = Event.objects.create(
            title="Test Event",
            host=self.host,
            description="Test Description",
            max_participants=5,
            start_time=now(),
            end_time=now() + timedelta(hours=2),
        )

        self.event_participant = EventParticipant.objects.create(
            event=self.event, user=self.participant
        )
        self.url = reverse("feedback", kwargs={"event_id": self.event.id})

    def test_create_feedback_success(self):
        self.client.force_authenticate(user=self.participant)
        response = self.client.post(
            self.url,
            {"event": self.event.id, "comment": "Great event!", "rating": 5},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 1)

    def test_create_feedback_event_not_found(self):
        self.client.force_authenticate(user=self.participant)
        url = reverse("feedback", kwargs={"event_id": 101})
        response = self.client.post(
            url, {"comment": "Great event!", "rating": 5}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_feedback_duplicate(self):
        self.client.force_authenticate(user=self.participant)
        Feedback.objects.create(
            event=self.event,
            user=self.participant,
            comment="Great event!",
            rating=5,
        )
        response = self.client.post(
            self.url, {"comment": "Awesome event", "rating": 5}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Feedback.objects.count(), 1)

    def test_create_feedback_unauthenticated(self):
        response = self.client.post(
            self.url, {"comment": "Nice event", "rating": 4}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_feedback_list(self):
        Feedback.objects.create(
            event=self.event,
            user=self.participant,
            comment="Awesome!",
            rating=5,
        )
        self.client.force_authenticate(user=self.host)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)


class DeleteOldEventsTestCase(APITestCase):

    def setUp(self):
        self.url = reverse("run-delete-old-events")

    def test_delete_old_events_success(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Success check terminal "})
