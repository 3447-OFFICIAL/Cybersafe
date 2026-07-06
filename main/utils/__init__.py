import re
import logging
from datetime import datetime
from typing import Any, Optional
from django.http import HttpRequest
from django.utils import timezone
try:
    from main.models import AuditLog
except Exception:
    AuditLog = None

logger = logging.getLogger(__name__)


def log_audit_action(
    request: Optional[HttpRequest],
    admin_user: Any,
    action: str,
    resource_type: str,
    resource_id: Optional[Any] = None,
    details: Optional[dict[str, Any]] = None,
) -> None:
    """Log admin actions for audit trail."""
    try:
        details = details or {}
        ip_address = details.get('ip_address') or (get_client_ip(request) if request else '127.0.0.1')
        user_agent = details.get('user_agent') or (request.META.get('HTTP_USER_AGENT', 'Django App') if request else 'Django App')

        if AuditLog is not None:
            AuditLog.objects.create(
                admin_user=admin_user,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else '',
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        else:
            logger.warning("AuditLog model not available; skipping DB audit insert: %s %s", admin_user, action)
    except Exception as e:
        logger.exception("Failed to log audit action")


def log_security_event(event_type: str, severity: str, description: str, request: Optional[HttpRequest] = None) -> None:
    """Log security-related events for monitoring dashboard."""
    try:
        # Import the SecurityEvent model from main.models
        from main.models import SecurityEvent

        ip_address = get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown') if request else 'System'

        event = SecurityEvent.objects.create(
            event_type=event_type,
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent,
            description=description,
            timestamp=timezone.now(),
        )
        logger.info(f"MONITORING: Logged {event_type} event: {description}")
    except Exception:
        logger.exception("Failed to log security event")


def get_client_ip(request: HttpRequest) -> str:
    """Get client IP address from request, respecting X-Forwarded-For if present."""
    if not request:
        return '127.0.0.1'
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('X-Forwarded-For')
    if x_forwarded_for:
        # X-Forwarded-For may contain a comma-separated list; client is first
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


def sanitize_input(text: Optional[str] | None) -> Optional[str]:
    """Sanitize user input to prevent XSS and injection attacks.

    Prefers `bleach` if available; otherwise falls back to a conservative
    regex-based cleanup.
    """
    if not text:
        return text

    try:
        import bleach

        cleaned = bleach.clean(text, strip=True)
        return cleaned.strip()
    except Exception:
        # Fallback: conservative regex-based cleaning
        text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        dangerous_tags = ['javascript:', 'vbscript:', 'onload', 'onerror', 'onclick']
        for tag in dangerous_tags:
            text = text.replace(tag, '')
        text = re.sub(r'[<>]', '', text)
        return text.strip()


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    pattern = r'^[\+]?[1-9][\d]{0,15}$'
    return re.match(pattern, phone) is not None


def get_severity_color(severity: str) -> str:
    """Get color class for severity level"""
    colors = {
        'low': 'success',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'danger'
    }
    return colors.get(severity, 'secondary')


def get_severity_icon(severity: str) -> str:
    """Get icon for severity level"""
    icons = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🟠',
        'critical': '🔴'
    }
    return icons.get(severity, '⚪')


def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    now = timezone.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hours ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minutes ago"
    else:
        return "Just now"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
