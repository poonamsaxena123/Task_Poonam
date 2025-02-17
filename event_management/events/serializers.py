from rest_framework import serializers
from .models import Event, EventParticipant, Invitation, Feedback
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class EventSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'

class EventParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = EventParticipant
        fields = '__all__'

class InvitationSerializer(serializers.ModelSerializer):
    inviter = UserSerializer(read_only=True)
    invitee = UserSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = '__all__'