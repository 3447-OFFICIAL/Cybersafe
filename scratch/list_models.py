import os
import sys
import django
from dotenv import load_dotenv
from google import genai

# Load .env
load_dotenv()

# Add project root
project_root = r"e:\Cyber-Safe-Portal"

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Django setup
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'cysafe_project.settings'
)

django.setup()

from main.models import ChatbotConfig
from chatbot.gemini_client import set_client_config

print("\n--- Gemini Configuration Check ---")

config = ChatbotConfig.objects.first()

if not config:
    print("No ChatbotConfig found.")
    exit()

# Load API key from .env
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("No GEMINI_API_KEY found in .env")
    exit()

# Initialize new SDK client
client = genai.Client(api_key=api_key)

# Initialize your chatbot client
set_client_config(
    api_key=api_key,
    model_name=config.gemini_model or "gemini-2.0-flash"
)

print(f"Using API Key: {api_key[:10]}...")
print(f"Configured Model: {config.gemini_model}")

# List available models
try:
    print("\n--- Available Models ---")

    models = client.models.list()

    for model in models:
        model_name = getattr(model, "name", "Unknown")

        print(f"Model: {model_name}")

except Exception as e:
    print(f"\nError listing models:")
    print(e)