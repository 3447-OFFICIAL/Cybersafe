from django.core.management.base import BaseCommand
from main.models import CyberCrime

class Command(BaseCommand):
    help = 'Delete crime with type "type 12"'

    def handle(self, *args, **options):
        try:
            # Find the crime
            crime = CyberCrime.objects.get(type="type 12")
            self.stdout.write(f"Found crime: {crime.type} (ID: {crime.id})")
            
            # Delete it
            crime.delete()
            self.stdout.write(
                self.style.SUCCESS("✅ Crime 'type 12' has been deleted successfully!")
            )
            
        except CyberCrime.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("❌ Crime with type 'type 12' not found in database.")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error deleting crime: {e}")
            ) 