from rest_framework.permissions import SAFE_METHODS, BasePermission
from.models import Event


class My_Permission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.host == request.user

 
class HostListPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method != "GET":
            return True  
        event_id = view.kwargs.get("event_id")
        if not event_id:
            return False
        try:
            event = Event.objects.get(id=event_id)
            return event.host == request.user
        except Event.DoesNotExist:
            return False




