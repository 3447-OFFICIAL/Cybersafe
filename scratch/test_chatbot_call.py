import os
import sys
import django
import google.generativeai as genai
import time

# Add project root to sys.path
project_root = r"e:\Cyber-Safe-Portal"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cysafe_project.settings')
django.setup()

from main.models import ChatbotConfig

config = ChatbotConfig.objects.first()
if config and config.gemini_api_key:
    genai.configure(api_key=config.gemini_api_key)
    model_id = config.gemini_model or 'gemini-2.5-flash'
    print(f"Testing model: {model_id}")
    
    try:
        model = genai.GenerativeModel(model_id)
        prompt = f"{config.system_prompt}\n\nUser: hello\n\nAssistant:"
        print("Sending prompt...")
        response = model.generate_content(prompt)
        print("Response received:")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No ChatbotConfig or API Key found.")
