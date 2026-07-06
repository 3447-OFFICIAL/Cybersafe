"""
Management command to fix HTML-encoded characters in existing crime records
"""
from django.core.management.base import BaseCommand
import html
from main.models import CyberCrime


class Command(BaseCommand):
    help = 'Fix HTML-encoded characters in existing crime records'

    def handle(self, *args, **options):
        self.stdout.write("Fixing HTML-encoded characters in existing crimes...")
        
        crimes = CyberCrime.objects.all()
        fixed_count = 0

        for crime in crimes:
            updated = False
            
            # Unescape the type field
            if crime.type:
                unescaped_type = html.unescape(crime.type)
                if unescaped_type != crime.type:
                    crime.type = unescaped_type
                    updated = True
                    self.stdout.write(f"  Fixed type: {crime.type}")
            
            # Unescape the description field
            if crime.description:
                unescaped_desc = html.unescape(crime.description)
                if unescaped_desc != crime.description:
                    crime.description = unescaped_desc
                    updated = True
                    self.stdout.write(f"  Fixed description for: {crime.type}")
            
            # Unescape how_it_works
            if crime.how_it_works:
                unescaped = html.unescape(crime.how_it_works)
                if unescaped != crime.how_it_works:
                    crime.how_it_works = unescaped
                    updated = True
            
            # Unescape impact
            if crime.impact:
                unescaped = html.unescape(crime.impact)
                if unescaped != crime.impact:
                    crime.impact = unescaped
                    updated = True
            
            # Unescape solution
            if crime.solution:
                unescaped = html.unescape(crime.solution)
                if unescaped != crime.solution:
                    crime.solution = unescaped
                    updated = True
            
            # Unescape prevention tips
            for i in range(1, 7):
                field_name = f'prevention_tip_{i}'
                field_value = getattr(crime, field_name, None)
                if field_value:
                    unescaped = html.unescape(field_value)
                    if unescaped != field_value:
                        setattr(crime, field_name, unescaped)
                        updated = True
            
            # Unescape reporting steps
            for i in range(1, 7):
                field_name = f'reporting_step_{i}'
                field_value = getattr(crime, field_name, None)
                if field_value:
                    unescaped = html.unescape(field_value)
                    if unescaped != field_value:
                        setattr(crime, field_name, unescaped)
                        updated = True
            
            if updated:
                crime.save()
                fixed_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n✅ Fixed {fixed_count} crime records'))
        self.stdout.write("All HTML entities have been converted back to normal characters")
