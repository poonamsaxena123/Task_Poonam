import re

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Event, EventParticipant, Feedback, Invitation


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
        
        
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate_password(self, value):
     
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")

        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

   
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")

        
        if not re.search(r'\d', value):
            
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*]', value):
            raise serializers.ValidationError("Password must contain at least one special character--> !@#$%^&*")


        return value