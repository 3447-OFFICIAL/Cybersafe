from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
import os
import json


class AdminUser(AbstractUser):
    """Custom admin user model with enhanced security"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        from .utils import validate_email, validate_phone
        super().clean()
        if self.email and not validate_email(self.email):
            raise ValidationError({'email': 'Invalid email format.'})
        if self.phone and not validate_phone(self.phone):
            raise ValidationError({'phone': 'Invalid phone format.'})
    is_active = models.BooleanField(default=True)
    login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'admin_users'


class CyberCrime(models.Model):
    """Model for storing cyber crime information"""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    CATEGORY_CHOICES = [
        ('csam', 'Child Pornography/ Child sexually abusive material (CSAM)'),
        ('cyber_bullying', 'Cyber Bullying'),
        ('cyber_stalking', 'Cyber stalking'),
        ('cyber_grooming', 'Cyber Grooming'),
        ('job_fraud', 'Online Job Fraud'),
        ('online_sextortion', 'Online Sextortion'),
        ('vishing', 'Vishing'),
        ('sexting', 'Sexting'),
        ('smshing', 'Smshing'),
        ('sim_swap', 'SIM Swap Scam'),
        ('card_fraud', 'Debit/Credit Card Fraud'),
        ('identity_theft', 'Impersonation and Identity Theft'),
        ('phishing', 'Phishing'),
        ('spamming', 'Spamming'),
        ('ransomware', 'Ransomware'),
        ('malware', 'Virus, Worms & Trojans'),
        ('data_breach', 'Data Breach'),
        ('dos_ddos', 'Denial Of Services /Distributed DoS'),
        ('website_defacement', 'Website Defacement'),
        ('cyber_squatting', 'Cyber-Squatting'),
        ('pharming', 'Pharming'),
        ('cryptojacking', 'Cryptojacking'),
        ('drug_trafficking', 'Online Drug Trafficking'),
        ('espionage', 'Espionage'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    
    # Detailed Information
    how_it_works = models.TextField(blank=True, null=True)
    impact = models.TextField(blank=True, null=True)
    solution = models.TextField(blank=True, null=True)
    
    # Image fields
    banner_image = models.ImageField(upload_to='crime_banners/', blank=True, null=True, help_text="Banner image for the crime post")
    
    # Prevention Tips & Reporting Steps - JSON storage for dynamic lists
    prevention_tips = models.JSONField(default=list, blank=True, help_text="List of prevention tips")
    reporting_steps = models.JSONField(default=list, blank=True, help_text="List of reporting steps")
    
    # Semantic Search Fields
    keywords = models.JSONField(default=list, blank=True, help_text="List of keywords for semantic search")
    tags = models.JSONField(default=list, blank=True, help_text="List of short display tags")
    related_domains = models.JSONField(default=list, blank=True, help_text="List of related domains associated with the threat")
    
    learn_more_clicks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cybercrime_data'
        ordering = ['-created_at']

    def __str__(self):
        return self.type
    
    def get_prevention_tips_count(self):
        """Count non-empty prevention tips"""
        return len(self.get_prevention_tips_list())
    
    def get_reporting_steps_count(self):
        """Count non-empty reporting steps"""
        return len(self.get_reporting_steps_list())
    
    def get_prevention_tips_list(self):
        """Get prevention tips as a list with fallback mechanism"""
        tips = [tip for tip in (self.prevention_tips or []) if tip and str(tip).strip()]
        if tips:
            return tips

        # Fallback mechanism if no tips are provided
        return self.get_default_prevention_tips()

    @classmethod
    def get_default_prevention_tips(cls):
        return [
            "Never share your OTP, PIN, or passwords with anyone.",
            "Use strong, unique passwords for different accounts.",
            "Enable two-factor authentication (2FA) wherever possible.",
            "Stay vigilant against suspicious links and emails."
        ]
    
    def get_reporting_steps_list(self):
        """Get reporting steps as a list with fallback mechanism"""
        steps = [step for step in (self.reporting_steps or []) if step and str(step).strip()]
        if steps:
            return steps
            
        # Fallback mechanism if no steps are provided
        return self.get_default_reporting_steps()

    @classmethod
    def get_default_reporting_steps(cls):
        return [
            "Immediately report the incident on www.cybercrime.gov.in",
            "Call the National Cyber Crime Helpline number 1930.",
            "Preserve all evidence like screenshots, emails, and transaction IDs.",
            "Inform your bank or financial institution if financial loss is involved."
        ]

    def get_how_it_works_list(self):
        """Get a crime-specific attack narrative as a list of steps."""
        if self.how_it_works:
            steps = [step.strip() for step in self.how_it_works.splitlines() if step and step.strip()]
            if steps:
                return steps

        return self.get_default_how_it_works()

    def get_default_how_it_works(self):
        """Build a short, category-aware attack narrative."""
        category_map = {
            'phishing': [
                'The attacker impersonates a trusted brand, support desk, or bank to lure the victim into opening a malicious link or attachment.',
                'The victim is pushed to submit credentials, OTPs, or payment details on a fake login or payment page.',
                'Captured access is used to steal funds, hijack accounts, or move laterally into related services.'
            ],
            'ransomware': [
                'The attack usually begins with a malicious email, compromised download, or exposed remote service that delivers the payload.',
                'Once executed, the malware encrypts files, disables recovery options, and may spread to shared systems or backups.',
                'The attacker demands payment and threatens data leakage or permanent loss if the ransom is not paid.'
            ],
            'cyber_bullying': [
                'The offender targets the victim through repeated harassment, impersonation, or humiliating posts across social platforms.',
                'Messages, images, or comments are amplified to pressure the victim emotionally or damage reputation.',
                'The abuse can escalate into stalking, account compromise, or coordinated reporting abuse across multiple accounts.'
            ],
            'identity_theft': [
                'Personal details are collected from leaks, social media, phishing, or insecure documents.',
                'The attacker uses the stolen identity to open accounts, request services, or pass verification checks.',
                'Financial fraud, fake registrations, and long-term account abuse follow once the identity is trusted by systems or people.'
            ],
            'job_fraud': [
                'The victim is approached with a fake job offer, interview, or recruitment message that looks legitimate.',
                'The attacker asks for upfront fees, identity documents, or banking details as part of the hiring process.',
                'The scam ends with money loss, identity misuse, or resale of the collected information.'
            ],
            'sim_swap': [
                'The attacker gathers personal details from leaks, phishing, or social engineering to impersonate the victim.',
                'Using the stolen data, the criminal convinces the telecom provider to move the number to a new SIM.',
                'Once the number is hijacked, the attacker intercepts OTPs and resets banking or account passwords.'
            ],
            'card_fraud': [
                'Card details are captured through skimmers, fake checkout pages, phishing, or malware.',
                'The attacker performs unauthorized online purchases, wallet top-ups, or card-not-present transactions.',
                'Fraud is sustained until the card is blocked or the stolen credentials are detected by the issuer.'
            ],
        }

        category = (self.category or '').strip().lower()
        title = (self.type or 'the threat').strip()
        summary = self.description.strip() if self.description else ''

        steps = category_map.get(category, [
            f'The attacker studies {title.lower()} to find the easiest entry point, such as trust gaps, exposed services, or human error.',
            f'The compromise is carried out with social engineering, credential theft, malicious content, or a weakly protected workflow tied to {title.lower()}.',
            'The attacker uses the access to steal data, disrupt services, extort the victim, or move into connected accounts and systems.'
        ])

        if summary:
            steps[0] = summary

        return steps

    def get_impact_list(self):
        """Get a list of impacts, using the database impact field or a category-aware default list."""
        if self.impact:
            points = [p.strip() for p in self.impact.splitlines() if p and p.strip()]
            if points:
                return points
        return self.get_default_impact()

    def get_default_impact(self):
        category_map = {
            'phishing': [
                'Unauthorized financial transactions and immediate loss of personal funds.',
                'Compromise of primary email and social media accounts leading to reputation damage.',
                'Secondary attacks targeting your contacts using your hijacked identity.'
            ],
            'identity_theft': [
                'Creation of fraudulent bank accounts or loans in your name, causing severe debt liabilities.',
                'Misuse of your government identity (e.g. Aadhaar) for acquiring illegal SIM cards or registering dummy businesses.',
                'Legal issues and police investigation involvement due to crime footprints registered in your name.'
            ],
            'sim_swap': [
                'Total loss of signal and mobile network access as control moves to the attacker.',
                'Bypassing of SMS-based two-factor authentication (2FA) for major banking portals.',
                'Unauthorized password resets on financial accounts and subsequent funds transfer.'
            ],
            'ransomware': [
                'Permanent loss of critical personal documents, databases, and media assets.',
                'Complete disruption of day-to-day operations and access to target devices.',
                'Leaking of confidential or sensitive data on public extort sites if demands are unmet.'
            ],
            'malware': [
                'Siphoning of keystrokes, personal passwords, and browser-saved banking credentials.',
                'Device becomes part of a malicious botnet used to attack third-party infrastructures.',
                'Hardware fatigue, high system temperatures, and unexpected software crashes.'
            ],
            'card_fraud': [
                'Direct financial depletion through unauthorized transactions and ATM withdrawals.',
                'Long-running, hard-to-detect subscription charges on dark web markets.',
                'Card blockage, leading to service denials and disruption of regular payments.'
            ],
            'job_fraud': [
                'Direct loss of registration fees, kit deposits, and training costs paid to fraudsters.',
                'Compromise of personal banking details and government identity cards during fake onboarding.',
                'Emotional distress and waste of valuable job-seeking time and energy.'
            ]
        }
        category = (self.category or '').strip().lower()
        title = (self.type or 'the threat').strip()
        
        return category_map.get(category, [
            f'Significant exposure and unauthorized access to your private profile linked to {title.lower()}.',
            f'Direct or indirect financial damage arising from threat exploitation vectors.',
            f'Reputation loss and legal security review necessity across related online accounts.'
        ])

    def get_solution_list(self):
        """Get a list of solutions/remediations, using the database solution field or a category-aware default list."""
        if self.solution:
            steps = [s.strip() for s in self.solution.splitlines() if s and s.strip()]
            if steps:
                return steps
        return self.get_default_solution()

    def get_default_solution(self):
        category_map = {
            'phishing': [
                'Immediately change the passwords of any account whose credentials you entered.',
                'Activate multi-factor authentication (MFA) using authenticator apps rather than SMS.',
                'Report the fake phishing link to security portals like Google Safe Browsing and Netcraft.'
            ],
            'identity_theft': [
                'Lock/biometric block your Aadhaar card immediately on the official UIDAI mAadhaar app or website.',
                'File a formal cybercrime complaint at https://cybercrime.gov.in and save the acknowledgment copy.',
                'Notify your bank, credit bureau (CIBIL), and mobile operators to prevent unauthorized accounts.'
            ],
            'sim_swap': [
                'Contact your mobile network operator immediately to lock the SIM card and verify identity.',
                'Immediately inform your bank to freeze all online banking channels and UPI accounts.',
                'Change security questions and primary emails associated with your financial profile.'
            ],
            'ransomware': [
                'Disconnect the infected computer from the local network and internet immediately.',
                'Do not pay the ransom; instead, seek professional security guidance and check decryption tools.',
                'Restore non-infected systems using offline or external backups that were not connected to the network.'
            ],
            'malware': [
                'Run a full system scan using verified and up-to-date antivirus/anti-malware software.',
                'Review startup programs and uninstall any unrecognized applications or extensions.',
                'Reinstall the operating system if the threat persists or has compromised administrative access.'
            ],
            'card_fraud': [
                'Contact your bank immediately to block the compromised card and dispute the fraudulent charges.',
                'Set transaction limits and disable international/contactless payments on your cards.',
                'Switch to virtual cards or tokenize your card details on secure merchant systems.'
            ],
            'job_fraud': [
                'Stop all communication with the recruiters and do not pay any additional demands.',
                'Collect and document all chats, email receipts, and transaction records.',
                'File a complaint on the official cyber portal and contact your bank for chargeback if paid via card/UPI.'
            ]
        }
        category = (self.category or '').strip().lower()
        title = (self.type or 'the threat').strip()
        
        return category_map.get(category, [
            f'Identify and isolate the system or account compromised by the {title.lower()} threat.',
            'Rotate security credentials, revoke active sessions, and verify recovery settings.',
            'Report the threat incidents immediately to the National Cyber Crime Helpline (1930) or cybercrime.gov.in.'
        ])

    def get_images_count(self):
        """Count additional images from related model"""
        count = self.additional_images.count()
        return count if count > 0 else 2  # Reflect fallback count if empty
    
    def get_banner_image_url(self):
        """Get banner image URL with fallback"""
        if self.banner_image:
            return self.banner_image.url
        return "https://placehold.co/1200x600/1a1a2e/ffffff?text=Cyber+Safe+Portal+-+Crime+Analysis"

    def get_images_list(self):
        """Get additional images as a list of image URLs with fallback mechanism"""
        images = list(self.additional_images.all())
        if images:
            return [img.image.url for img in images]
        
        # Fallback mechanism if no additional images are provided
        return [
            "https://placehold.co/600x400/2a2a40/ffffff?text=Evidence+Analysis+1",
            "https://placehold.co/600x400/2a2a40/ffffff?text=Prevention+Graphics+2"
        ]


class CyberCrimeImage(models.Model):
    """Model for storing multiple images related to a cyber crime"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    crime = models.ForeignKey(CyberCrime, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='crime_images/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cybercrime_images'
        ordering = ['created_at']

    def __str__(self):
        return f"Image for {self.crime.type}"


class ChatbotConfig(models.Model):
    """Model for storing chatbot configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gemini_model = models.CharField(max_length=100, default='gemini-1.5-flash')
    system_prompt = models.TextField(default="You are a cybersecurity assistant focused on online safety, fraud prevention, cybercrime awareness, and digital protection.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chatbot_config'

    def __str__(self):
        return f"Chatbot Config - {self.gemini_model}"


class ChatbotConversation(models.Model):
    """Model for tracking chatbot conversations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_message = models.TextField()
    bot_response = models.TextField()
    response_time = models.FloatField(help_text="Response time in seconds")
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chatbot_conversations'
        ordering = ['-created_at']

    def __str__(self):
        return f"Conversation {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class AuditLog(models.Model):
    """Model for storing admin action audit logs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin_user = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']

class SecurityEvent(models.Model):
    """Model for tracking security-related events"""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    EVENT_TYPES = [
        ('failed_login', 'Failed Login Attempt'),
        ('rate_limit', 'Rate Limit Triggered'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('invalid_token', 'Invalid Token Attempt'),
        ('unauthorized_access', 'Unauthorized Access Attempt'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'security_events'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} - {self.severity} - {self.timestamp}"


class SystemUptime(models.Model):
    """Model for tracking system uptime"""
    start_time = models.DateTimeField(default=timezone.now)
    last_check = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_uptime'

    @property
    def duration(self):
        delta = timezone.now() - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"


class UniqueVisitor(models.Model):
    """Model for tracking unique website visitors by IP"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField(unique=True)
    first_visit = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'unique_visitors'

    def __str__(self):
        return self.ip_address

class SecurityQuestion(models.Model):
    CATEGORY_CHOICES = [
        ('password_security', 'Password Security'),
        ('phishing', 'Phishing & Scams'),
        ('social_engineering', 'Social Engineering'),
        ('mobile_security', 'Mobile Security'),
        ('banking_fraud', 'Banking Fraud'),
        ('privacy_protection', 'Privacy Protection'),
        ('public_wifi', 'Public WiFi'),
        ('upi_scams', 'UPI Scams'),
        ('device_security', 'Device Security'),
        ('safe_browsing', 'Safe Browsing')
    ]
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]
    text = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='phishing')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1, choices=[('A','A'), ('B','B'), ('C','C'), ('D','D')])
    explanation = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.text[:50]

class SecurityAssessmentResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    score = models.IntegerField()
    total = models.IntegerField()
    risk_level = models.CharField(max_length=50)
    category_scores = models.JSONField(default=dict)
    weaknesses = models.JSONField(default=list)
    strengths = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assessment {self.id} - Score: {self.score}"
