import os
import django
import time
import google.generativeai as genai

import sys
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cysafe_project.settings')
django.setup()

from main.models import ChatbotConfig
from gemini_client import set_client_config

def test_all_models():
    config = ChatbotConfig.objects.first()
    if not config or not config.gemini_api_key:
        print("Error: No API key found in database.")
        return

    print(f"Using API Key: {config.gemini_api_key[:10]}...")
    genai.configure(api_key=config.gemini_api_key)

    models_to_test = [
        'gemini-2.0-flash',
        'gemini-2.5-flash',
        'gemini-flash-latest',
        'gemini-2.0-flash-lite',
        'gemini-1.5-pro'
    ]

    working_model = None

    for m_name in models_to_test:
        print(f"\nTesting model: {m_name}")
        try:
            model = genai.GenerativeModel(
                model_name=m_name,
                system_instruction="You are a helper. Answer shortly."
            )
            response = model.generate_content("Hello, wave at me.")
            if response and response.text:
                print(f"SUCCESS! {m_name} is working.")

                safe_text = response.text.encode(
                    'ascii',
                    'ignore'
                ).decode('ascii')

                print(f"Response (ASCII safe): {safe_text}")
                working_model = m_name
                break
            else:
                print(f"FAILED: {m_name} returned empty response.")
        except Exception as e:
            error_msg = str(e)
            if "Quota" in error_msg or "429" in error_msg:
                print(f"QUOTA ERROR: {m_name} is rate limited. (429)")
            elif "not found" in error_msg.lower() or "404" in error_msg:
                print(f"NOT FOUND: {m_name} is not available. (404)")
            elif "codec" in error_msg:
                print(f"SUCCESS! {m_name} is working (unicode issue).")
                working_model = m_name
                break
            else:
                print(f"ERROR: {m_name} failed with: {error_msg}")

    if working_model:
        print(f"\nRecommended action: Setting database model to {working_model}")
        config.gemini_model = working_model
        config.save()
        print("Database updated.")

        set_client_config(
            api_key=config.gemini_api_key,
            model_name=working_model
        )

    else:

        print("\nCRITICAL: No models are working right now.")
        print("Please wait 1-2 minutes for the quota reset or check API key.")