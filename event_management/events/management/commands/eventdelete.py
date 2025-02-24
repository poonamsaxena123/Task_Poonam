from django.core.management.base import BaseCommand
from django.utils import timezone  
from events.models import Event
from datetime import timedelta


class Command(BaseCommand):
    help = "Delete Events Older than One Month"

    def handle(self, *args, **options):
        try:
            one_month_ago = timezone.now() - timedelta(days=30)
            events = Event.objects.filter(created_at__lt=one_month_ago)
            
            if not events.exists():
                return self.stdout.write(self.style.WARNING("No events found older than one month."))

            count = events.delete()
            return self.stdout.write(self.style.SUCCESS(f"{count} event(s) deleted successfully."))
        except Exception as e:
            return self.stdout.write(self.style.ERROR(f"Error: {str(e)} - Event deletion failed."))

        