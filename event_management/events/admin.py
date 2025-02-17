from django.contrib import admin
from .models import Event, EventParticipant, Invitation, Feedback

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'start_time', 'end_time', 'location', 'max_participants')
    search_fields = ('title', 'host__username')
    list_filter = ('start_time', 'end_time')


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'event')
    search_fields = ('user__username', 'event__title')


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('event', 'inviter', 'invitee', 'status', 'sent_at', 'responded_at')
    list_filter = ('status',)
    search_fields = ('inviter__username', 'invitee__username', 'event__title')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'rating', 'comment')
    list_filter = ('rating',)
    search_fields = ('user__username', 'event__title')
