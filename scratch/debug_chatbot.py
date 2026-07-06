import os
import sys
import django

project_root = r"e:\Cyber-Safe-Portal"

if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cysafe_project.settings')

django.setup()

from main.models import ChatbotConversation, ChatbotConfig
from dotenv import load_dotenv
load_dotenv()

print("--- Chatbot Config ---")

config = ChatbotConfig.objects.first()

if config:
    print(f"Model ID: {config.gemini_model}")

    api_key = os.getenv("GEMINI_API_KEY")

    print(f"ENV API Key present: {'Yes' if api_key else 'No'}")

    if api_key:
        print(f"API Key start: {api_key[:10]}...")

    print(f"System Prompt length: {len(config.system_prompt)}")

else:
    print("No ChatbotConfig found.")

print("\n--- Last 5 Conversations ---")

convs = ChatbotConversation.objects.all().order_by('-created_at')[:5]

for c in convs:
    print(f"ID: {c.id}")
    print(f"Time: {c.created_at}")
    print(f"User: {c.user_message[:50]}...")
    print(f"Success: {c.success}")
    print(f"Error: {c.error_message}")
    print("-" * 20)