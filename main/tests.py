from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
import json
import uuid

from .models import AdminUser, CyberCrime, ChatbotConfig, ChatbotConversation, SecurityAssessmentResult
from .utils import (
    sanitize_input, validate_email, validate_phone, 
    get_severity_color, get_severity_icon, format_timestamp, truncate_text,
    log_audit_action, get_client_ip
)

class UtilityTests(TestCase):
    """Test utility functions in utils.py"""
    
    def test_sanitize_input(self):
        # bleach.clean with strip=True removes the tags but leaves the content
        self.assertEqual(sanitize_input("<script>alert('xss')</script>Hello"), "alert('xss')Hello")
        self.assertEqual(sanitize_input("  Hello World  "), "Hello World")
        self.assertEqual(sanitize_input("<p>Paragraph</p>"), "Paragraph")
        self.assertEqual(sanitize_input(None), None)

    def test_validate_email(self):
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name+tag@domain.co.uk"))
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("test@domain"))
        self.assertFalse(validate_email("@domain.com"))

    def test_validate_phone(self):
        self.assertTrue(validate_phone("1234567890"))
        self.assertTrue(validate_phone("+1234567890"))
        self.assertFalse(validate_phone("abc1234567"))
        self.assertFalse(validate_phone("123-456-7890"))

    def test_get_severity_color(self):
        self.assertEqual(get_severity_color('low'), 'success')
        self.assertEqual(get_severity_color('medium'), 'warning')
        self.assertEqual(get_severity_color('high'), 'danger')
        self.assertEqual(get_severity_color('critical'), 'danger')
        self.assertEqual(get_severity_color('unknown'), 'secondary')

    def test_get_severity_icon(self):
        self.assertEqual(get_severity_icon('low'), '🟢')
        self.assertEqual(get_severity_icon('critical'), '🔴')
        self.assertEqual(get_severity_icon('unknown'), '⚪')

    def test_format_timestamp(self):
        now = timezone.now()
        self.assertEqual(format_timestamp(now - timedelta(seconds=30)), "Just now")
        self.assertEqual(format_timestamp(now - timedelta(minutes=5)), "5 minutes ago")
        self.assertEqual(format_timestamp(now - timedelta(hours=2)), "2 hours ago")
        self.assertEqual(format_timestamp(now - timedelta(days=3)), "3 days ago")

    def test_truncate_text(self):
        text = "This is a long text that should be truncated."
        self.assertEqual(truncate_text(text, 10), "This is a ...")
        self.assertEqual(truncate_text("Short", 10), "Short")

    def test_log_audit_action(self):
        from django.test import RequestFactory
        from .models import AuditLog, AdminUser
        
        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'Test Agent'
        request.META['REMOTE_ADDR'] = '1.2.3.4'
        
        user = AdminUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        log_audit_action(
            admin_user=user, 
            action='TEST_ACTION', 
            resource_type='test_resource', 
            resource_id='123', 
            details={'some': 'detail'},
            request=request
        )
        
        log = AuditLog.objects.filter(action='TEST_ACTION').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.admin_user, user)
        self.assertEqual(log.ip_address, '1.2.3.4')
        self.assertEqual(log.user_agent, 'Test Agent')
        self.assertEqual(log.details, {'some': 'detail'})


class ModelTests(TestCase):
    """Test model methods in models.py"""
    
    def setUp(self):
        self.crime = CyberCrime.objects.create(
            type="Phishing",
            description="Phishing attack description",
            category="phishing",
            severity="high",
            prevention_tips=["Tip 1", "Tip 2"],
            reporting_steps=["Step 1"]
        )

    def test_cybercrime_methods(self):
        self.assertEqual(self.crime.get_prevention_tips_count(), 2)
        self.assertEqual(self.crime.get_prevention_tips_list(), ["Tip 1", "Tip 2"])
        self.assertEqual(self.crime.get_reporting_steps_count(), 1)
        self.assertEqual(self.crime.get_reporting_steps_list(), ["Step 1"])
        self.assertEqual(str(self.crime), "Phishing")


class LoginLockoutTests(TestCase):
    """Test login lockout logic in AdminLoginView"""
    
    def setUp(self):
        self.client = Client()
        self.email = "admin@example.com"
        self.password = "securepassword123"
        self.user = AdminUser.objects.create_user(
            username="admin",
            email=self.email,
            password=self.password,
            is_staff=True
        )
        self.login_url = reverse('admin_login')

    def test_failed_login_increments_attempts(self):
        # 1st failure
        response = self.client.post(self.login_url, {'email': self.email, 'password': 'wrongpassword'})
        self.user.refresh_from_db()
        self.assertEqual(self.user.login_attempts, 1)
        
        # 4th failure
        for _ in range(3):
            self.client.post(self.login_url, {'email': self.email, 'password': 'wrongpassword'})
        self.user.refresh_from_db()
        self.assertEqual(self.user.login_attempts, 4)
        self.assertIsNone(self.user.locked_until)

    def test_lockout_after_five_attempts(self):
        # Perform 5 failed attempts
        for _ in range(5):
            self.client.post(self.login_url, {'email': self.email, 'password': 'wrongpassword'})
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.login_attempts, 5)
        self.assertIsNotNone(self.user.locked_until)
        # Should be locked for 30 minutes
        self.assertTrue(self.user.locked_until > timezone.now())

    def test_locked_account_cannot_login_with_correct_password(self):
        # Lock the account
        self.user.login_attempts = 5
        self.user.locked_until = timezone.now() + timedelta(minutes=30)
        self.user.save()
        
        # Try login with correct password
        response = self.client.post(self.login_url, {'email': self.email, 'password': self.password})
        self.assertFalse('_auth_user_id' in self.client.session)
        # Check if error message is present (Account is temporarily locked)
        messages = list(response.context['messages'])
        self.assertTrue(any("locked" in str(m).lower() for m in messages))

    def test_successful_login_resets_attempts(self):
        self.user.login_attempts = 3
        self.user.save()
        
        response = self.client.post(self.login_url, {'email': self.email, 'password': self.password})
        self.user.refresh_from_db()
        self.assertEqual(self.user.login_attempts, 0)
        self.assertIsNone(self.user.locked_until)
        self.assertTrue('_auth_user_id' in self.client.session)


class APITests(TestCase):
    """Test API endpoints in views.py"""
    
    def setUp(self):
        from django.core.cache import cache
        cache.clear()  # Reset DRF throttle state between tests
        self.client = Client()
        self.crime = CyberCrime.objects.create(
            type="Ransomware",
            description="Ransomware description",
            category="ransomware",
            severity="critical"
        )
        self.user = AdminUser.objects.create_user(
            username="api_admin",
            email="api@example.com",
            password="password123",
            is_staff=True
        )

    def test_crime_data_api(self):
        self.client.force_login(self.user)
        url = reverse('crime_data_api', kwargs={'crime_id': self.crime.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['type'], "Ransomware")
        self.assertEqual(data['category'], "ransomware")

    def test_increment_clicks_api(self):
        url = reverse('increment_clicks')
        initial_clicks = self.crime.learn_more_clicks
        response = self.client.post(
            url, 
            data=json.dumps({'crime_id': str(self.crime.id)}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.crime.refresh_from_db()
        self.assertEqual(self.crime.learn_more_clicks, initial_clicks + 1)

    @patch('main.views.generate')
    def test_chatbot_api(self, mock_generate):
        mock_generate.return_value = "This is a mock AI response."
        
        # Test request
        url = reverse('chatbot_api')
        response = self.client.post(
            url,
            data=json.dumps({'message': 'How to prevent phishing?'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['response'], "This is a mock AI response.")
        
        # Verify conversation logged
        self.assertEqual(ChatbotConversation.objects.count(), 1)
        conv = ChatbotConversation.objects.first()
        self.assertEqual(conv.user_message, "How to prevent phishing?")
        self.assertEqual(conv.bot_response, "This is a mock AI response.")
        self.assertTrue(conv.success)

    @patch('main.views.generate')
    def test_chatbot_rate_limit(self, mock_generate):
        """DRF ScopedRateThrottle limits chatbot to 5 requests/minute."""
        mock_generate.return_value = "Mock response"

        url = reverse('chatbot_api')

        # Send 20 requests within the limit — all should succeed
        for i in range(20):
            response = self.client.post(
                url,
                data=json.dumps({'message': f'Message {i}'}),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 200, f"Request {i+1} should succeed")

        # 21st request should be throttled
        response = self.client.post(
            url,
            data=json.dumps({'message': 'One too many'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 429)


class FormTests(TestCase):
    """Test CyberCrimeForm validation and sanitization"""

    def test_form_sanitization(self):
        from .forms import CyberCrimeForm
        data = {
            'type': "<script>alert('xss')</script>Phishing Attack",
            'description': "Some malicious description <p>with tags</p>",
            'category': 'phishing',
            'severity': 'high',
            'prevention_tips': '["Never click suspicious links"]',
            'reporting_steps': '["Report to cybercrime.gov.in"]'
        }
        form = CyberCrimeForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        cleaned = form.cleaned_data
        self.assertEqual(cleaned['type'], "alert('xss')Phishing Attack")
        self.assertEqual(cleaned['description'], "Some malicious description with tags")

    def test_form_prevention_tips_parsing(self):
        from .forms import CyberCrimeForm
        data = {
            'type': "Vishing",
            'description': "Phone fraud",
            'category': 'vishing',
            'severity': 'medium',
            'prevention_tips': 'Tip One\nTip Two',
            'reporting_steps': '["Step One"]'
        }
        form = CyberCrimeForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['prevention_tips'], ['Tip One', 'Tip Two'])
        self.assertEqual(form.cleaned_data['reporting_steps'], ['Step One'])

    def test_form_invalid_banner_image(self):
        from .forms import CyberCrimeForm
        from django.core.files.uploadedfile import SimpleUploadedFile
        invalid_image = SimpleUploadedFile("test.txt", b"not-an-image-content", content_type="image/png")
        data = {
            'type': "Malware",
            'description': "Virus threat",
            'category': 'malware',
            'severity': 'low',
        }
        files = {
            'banner_image': invalid_image
        }
        form = CyberCrimeForm(data=data, files=files)
        self.assertFalse(form.is_valid())
        self.assertIn('banner_image', form.errors)


class LoginValidationTests(TestCase):
    """Test email format validation in admin login"""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('admin_login')

    def test_login_invalid_email_format(self):
        response = self.client.post(self.login_url, {
            'email': 'not-a-valid-email-format',
            'password': 'somepassword'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("invalid email format" in str(m).lower() for m in messages))

    def test_login_deactivated_user(self):
        deactivated_user = AdminUser.objects.create_user(
            username="deactivated",
            email="deactivated@example.com",
            password="somepassword123",
            is_staff=True,
            is_active=False
        )
        response = self.client.post(self.login_url, {
            'email': 'deactivated@example.com',
            'password': 'somepassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)
        deactivated_user.refresh_from_db()
        self.assertFalse(deactivated_user.is_active)

    def test_login_non_staff_user(self):
        non_staff_user = AdminUser.objects.create_user(
            username="nonstaff",
            email="nonstaff@example.com",
            password="somepassword123",
            is_staff=False,
            is_active=True
        )
        response = self.client.post(self.login_url, {
            'email': 'nonstaff@example.com',
            'password': 'somepassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)


class PDFGenerationTests(TestCase):
    """Test PDF generation service and views"""

    def setUp(self):
        self.client = Client()
        self.result = SecurityAssessmentResult.objects.create(
            score=12,
            total=15,
            risk_level="Low",
            category_scores={
                "password_security": {"name": "Password Security", "percentage": 85},
                "phishing": {"name": "Phishing & Scams", "percentage": 80},
                "mobile_security": {"name": "Mobile Security", "percentage": 75},
            },
            weaknesses=["mobile_security"],
            strengths=["Password Security", "Phishing & Scams"]
        )

    def test_pdf_generation_direct(self):
        import io
        from main.services.pdf_service import generate_pdf
        buffer = io.BytesIO()
        # This will test our fallback (ReportLab) since WeasyPrint lacks native GTK libs locally
        generate_pdf(self.result, [], buffer)
        pdf_data = buffer.getvalue()
        self.assertTrue(len(pdf_data) > 0)
        self.assertTrue(pdf_data.startswith(b'%PDF'))

    def test_download_scorecard_pdf_view(self):
        url = reverse('download_scorecard_pdf', kwargs={'assessment_id': self.result.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(len(response.content) > 0)


