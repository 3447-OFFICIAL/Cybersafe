import os
import sys

# Setup Django environment
sys.path.append(r'e:\Cyber-Safe-Portal')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cysafe_project.settings")

import django
django.setup()

from main.models import AssessmentQuestion

questions = [
    {
        "category": "NETWORK",
        "text": "What is the primary purpose of a VPN?",
        "option_a": "To make your internet speed faster",
        "option_b": "To encrypt your internet traffic and hide your IP",
        "option_c": "To prevent viruses from entering your computer",
        "option_d": "To remember your passwords",
        "correct_option": "B",
        "explanation": "A VPN (Virtual Private Network) encrypts your data connection and masks your IP address, protecting your data from interception on public networks."
    },
    {
        "category": "PHISHING",
        "text": "You receive an email from 'IT Dept' asking you to verify your password. The link points to 'http://login-update-security.com'. What should you do?",
        "option_a": "Click the link and verify to avoid account suspension",
        "option_b": "Reply to the email and ask if it's legitimate",
        "option_c": "Report the email as phishing and do not click",
        "option_d": "Forward it to all your colleagues as a warning",
        "correct_option": "C",
        "explanation": "IT departments will never ask for your password. The URL is suspicious and not your company's official domain."
    },
    {
        "category": "DEVICE",
        "text": "Why is it dangerous to plug in a random USB drive you found?",
        "option_a": "It could fry your computer's motherboard",
        "option_b": "It might contain malicious software that auto-installs",
        "option_c": "It could be illegal",
        "option_d": "The files on it might be copyrighted",
        "correct_option": "B",
        "explanation": "USB drop attacks are common. Malicious USBs can contain malware or scripts that automatically execute as soon as plugged in."
    },
    {
        "category": "SOCIAL",
        "text": "What type of information is generally safe to share publicly on social media?",
        "option_a": "Your mother's maiden name",
        "option_b": "Your current live location",
        "option_c": "A picture of your new driver's license",
        "option_d": "Your general hobbies and interests",
        "correct_option": "D",
        "explanation": "General hobbies are safe. Mother's maiden name, live location, and ID documents can be used for identity theft or physical tracking."
    },
    {
        "category": "PASSWORDS",
        "text": "What is a 'credential stuffing' attack?",
        "option_a": "Guessing passwords using a dictionary of words",
        "option_b": "Using stolen passwords from one site to log into other sites",
        "option_c": "Typing a password so fast it crashes the server",
        "option_d": "Calling support to reset a password",
        "correct_option": "B",
        "explanation": "Credential stuffing involves hackers taking email/password pairs breached from one site and automating login attempts on other popular sites."
    }
]

added = 0
for q in questions:
    obj, created = AssessmentQuestion.objects.get_or_create(text=q['text'], defaults=q)
    if created:
        added += 1
    
print(f"Added {added} new questions.")
