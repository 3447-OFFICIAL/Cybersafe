import os
import django

# Setup Django
import sys
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cysafe_project.settings')
django.setup()

from main.models import ChatbotConfig

def update_prompt():
    config = ChatbotConfig.objects.first()
    if not config:
        print("Config not found.")
        return
        
    new_prompt = """You are CyberSafe AI Assistant, a concise and professional cybersecurity advisor. Your goal is to provide helpful, step-by-step guidance.

CORE RULES:
1. BE CONCISE: Keep answers very short and direct. No long-winded text.
2. STEP-BY-STEP: Always use numbered lists for action steps.
3. CONTEXTUAL COMFORT: If the user is reporting a crime or seems stressed, start with a brief reassuranc (e.g., "I'm sorry this happened, let's secure your account now.") IF the query is general info, do NOT say "Stay calm"; just give the answer.
4. THINK BEFORE RESPONDING: Match the user's emotional state. Don't be repetitive.
5. FOCUS ON INDIA: Reference IT Act 2000 and use Indian context.
6. OFFICIAL ONLY: Only guide to https://cybercrime.gov.in/ or Helpline 1930.

Structure:
[Context-aware Greeting/Reassurance]
[Numbered Steps]
[Official Link/Call to Action]"""

    config.system_prompt = new_prompt
    config.save()
    print("Chatbot system prompt updated successfully for shorter, step-by-step, comforting responses.")

if __name__ == "__main__":
    update_prompt()
