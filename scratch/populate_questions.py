import os
import django
import sys

# Add the current directory to sys.path
sys.path.append(os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cysafe_project.settings')
django.setup()

from main.models import AssessmentQuestion

def populate_questions():
    questions = [
        {
            'text': 'How often do you change your primary banking password?',
            'category': 'passwords',
            'option_a': 'Every month',
            'option_b': 'Every 3-6 months',
            'option_c': 'Once a year',
            'option_d': 'Only when forced by the bank',
            'correct_option': 'B',
            'explanation': 'Regularly changing passwords every 3-6 months is a balanced approach to security.'
        },
        {
            'text': 'You receive an SMS saying your bank account is blocked and providing a link to "unblock" it. What do you do?',
            'category': 'phishing',
            'option_a': 'Click the link immediately to fix it',
            'option_b': 'Call the number in the SMS',
            'option_c': 'Ignore it and check your official banking app',
            'option_d': 'Forward the SMS to your friends',
            'correct_option': 'C',
            'explanation': 'Banks never send links via SMS to unblock accounts. Always use official apps or websites.'
        },
        {
            'text': 'Which of these makes a password "Strong"?',
            'category': 'passwords',
            'option_a': 'Your birthdate + your name',
            'option_b': '12345678',
            'option_c': 'At least 12 characters with mixed cases, numbers, and symbols',
            'option_d': 'A word from the dictionary',
            'correct_option': 'C',
            'explanation': 'Complexity and length are key to preventing brute-force attacks.'
        },
        {
            'text': 'What is the safest way to use public Wi-Fi at an airport?',
            'category': 'general',
            'option_a': 'Connect and login to your bank',
            'option_b': 'Connect only using a trusted VPN',
            'option_c': 'Public Wi-Fi is always safe if it has a password',
            'option_d': 'Share your personal hotspot with others',
            'correct_option': 'B',
            'explanation': 'Public Wi-Fi can be intercepted; a VPN encrypts your traffic.'
        }
    ]

    for q in questions:
        AssessmentQuestion.objects.create(**q)
    
    print(f"Successfully added {len(questions)} questions.")

if __name__ == "__main__":
    populate_questions()
