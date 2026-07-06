import os
import sys
import django

# Add project root to sys.path
project_root = r"e:\Cyber-Safe-Portal"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cysafe_project.settings')
django.setup()

from main.models import ChatbotConversation

print("\n--- Latest Failed Conversations ---")
convs = ChatbotConversation.objects.filter(success=False).order_by('-created_at')[:3]
for c in convs:
    print(f"ID: {c.id}")
    print(f"Time: {c.created_at}")
    print(f"User: {c.user_message}")
    print(f"Error: {c.error_message}")
    print("-" * 20)
