from django.db import models
from django.utils import timezone
import uuid

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
