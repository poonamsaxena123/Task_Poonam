from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.contrib.auth.models import User
from .models import Event, EventParticipant, Invitation, Feedback
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import EventSerializer, RegisterSerializer, EventParticipantSerializer, InvitationSerializer ,FeedbackSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now 
from rest_framework.pagination import PageNumberPagination  
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView,RetrieveDestroyAPIView, UpdateAPIView
from . permission import My_Permission, HostListPermission


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            email = serializer.validated_data['email']

            if User.objects.filter(username=username).exists():
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create(
                username=username,
                password=make_password(password),
                email=email
            )
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)
        


class EventListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer
    pagination_class = PageNumberPagination


    def post(self, request):
        try:
            serializer = EventSerializer(data=request.data)
            today = now().date()
            events_today = Event.objects.filter(host=request.user, created_at__date=today).count()

            if events_today >= 5:
                return Response(
                    {"detail": "You can only create 5 events per day."},status=status.HTTP_429_TOO_MANY_REQUESTS)

            if serializer.is_valid():
                serializer.save(host=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": f"Event creation failed: {str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
    def get_queryset(self):
        
        try:
            events = Event.objects.all()

            host = self.request.query_params.get('host')
            if host:
                events = events.filter(host__id=host)

            start_date = self.request.query_params.get('start_date')
            end_date = self.request.query_params.get('end_date')
            if start_date and end_date:
                events = events.filter(start_time__gte=start_date, end_time__lte=end_date)

            location = self.request.query_params.get('location')
            if location:
                events = events.filter(location__icontains=location)

            return events

        except Exception as e:
            return Response(
                {"error": f"Could not fetch events: {str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
class EventRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    
    permission_classes = [IsAuthenticated, My_Permission]
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        try:
            event = self.get_object()
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Event.DoesNotExist:
            return Response({"error": "Event not Exist"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": f"Something went wrong---> {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            event = self.get_object()
            serializer = EventSerializer(event, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": f"Something went wrong: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def delete(self, request, *args, **kwargs):
        try:
            event = self.get_object()  
            event.delete()
            return Response({"message": "Event deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return Response({"error": f"There is No Event Exists for that Host: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  
class EventParticipantCreate(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, event_id):
        user = request.user
        print("-----user",user.username ,"event_id---",event_id)
        
        event = Event.objects.filter(id=event_id).first()
        if not event:
            return Response({"error": "No event found"}, status=status.HTTP_404_NOT_FOUND)

        if event.max_participants <= event.eventparticipant_set.count():
            return Response({"error": "Event is full"}, status=status.HTTP_400_BAD_REQUEST)

        if EventParticipant.objects.filter(event=event, user=user).count() > 0:
            return Response({"error": "User already registered for this event"}, status=status.HTTP_400_BAD_REQUEST)

        event_participant = EventParticipant.objects.create(event=event, user=user)
        return Response(
            {"message": "Successfully registered for the event", "participant_id": event_participant.id},
            status=status.HTTP_201_CREATED
        )
        
        
class EventParticipantsList(APIView):
    permission_classes = [IsAuthenticated,HostListPermission]
    def get(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
            print("----->event",event)
        except Event.DoesNotExist:
            return Response({"error": "No event found"}, status=status.HTTP_404_NOT_FOUND)

        try:
           
            participants = EventParticipant.objects.filter(event=event)
            
            serializer = EventParticipantSerializer(participants, many=True)

            return Response(
                {"event_id": event_id, "participants": serializer.data},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response({"error": f"Something went wrong: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SendInvitationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, event_id):
        user = request.user
        print(user.username)
        event = Event.objects.filter(id=event_id).first()
        if not event:
            return Response({"error": "No event found"}, status=status.HTTP_404_NOT_FOUND)
    
        if request.user != event.host:
            return Response({"error": "Only the event host can send invitations."}, status=status.HTTP_403_FORBIDDEN)
        
        invitee_id = request.data.get("invitee")
        if not invitee_id:
            return Response({"error": "Invitee ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        invitation, created = Invitation.objects.get_or_create(
            event=event, inviter=request.user, invitee_id=invitee_id,
            defaults={"status": "PENDING"}
        )
        
        if not created:
            return Response({"error": "Invitation already sent."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(InvitationSerializer(invitation).data, status=status.HTTP_201_CREATED)


class ListInvitationsView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        user = request.user
        hosted_events = Event.objects.filter(host=user)
        print(f"---->hosted_events:{hosted_events}")
        if not hosted_events.exists():
            return Response(
                {"error": "Only event hosts can access this list."}
            )
        invitations = Invitation.objects.filter(event__in=hosted_events, status="PENDING")
        print(f"----->invitations: {invitations}")
        serializer = InvitationSerializer(invitations, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class RespondInvitationView(UpdateAPIView):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "event_id"

    def get_object(self):
        invitation = Invitation.objects.filter(event_id=self.kwargs["event_id"], invitee=self.request.user).first()

        if not invitation:
            raise NotFound("Invitation not found or you do not have permission.")

        return invitation

    def update(self, request, *args, **kwargs):
        invitation = self.get_object()
        status_choice = request.data.get("status")

        if status_choice not in {"ACCEPTED", "DECLINED"}:
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        invitation.status = status_choice
        invitation.responded_at = now()
        invitation.save(update_fields=["status", "responded_at"]) 

        return Response(self.get_serializer(invitation).data, status=status.HTTP_200_OK)

      
class GetUserDestroyListView(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def get(self, request, *args, **kwargs):
        print(f"User --------------->{request.user}")
        try:
            registered_events = Event.objects.filter(eventparticipant__user=request.user)
            print(f"----registered_events :{registered_events}")
            if not registered_events.exists():
                return Response(
                    {"message": "You are not registered for any events."},
                    status=status.HTTP_200_OK
                )
            serializer = EventSerializer(registered_events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"something went wrong -->{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, event_id):
        try:
            event = Event.objects.filter(id=event_id).first()
            print(f"event ---->{event}")
            if not event:
                return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

            participant = EventParticipant.objects.filter(user=request.user, event=event).first()
            print(f"participant ---->{participant}")
            if not participant:
                return Response({"error": "User is not registered for this event"}, status=status.HTTP_404_NOT_FOUND)

            participant.delete()
            return Response({"message": "You are unregistered from the event"}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return Response({"error": f"something wrong :--->{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
                
class FeedbackView(ListCreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated,HostListPermission]
    def get_queryset(self):
        event_id = self.kwargs.get("event_id")
        return Feedback.objects.filter(event_id=event_id)
    

    def post(self, request, *args, **kwargs):
        user = request.user
        event_id = self.kwargs["event_id"]
        print(f"event_id -->{event_id}")
        try:
            event = Event.objects.get(id=event_id)
            print(f"event---{event}")
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if not EventParticipant.objects.filter(event=event, user=user).exists():
            return Response(
                {"error": "You can only leave feedback if you attended the event."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if Feedback.objects.filter(event=event, user=user).exists():
            return Response(
                {"error": "You have already give feedback for this event."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
