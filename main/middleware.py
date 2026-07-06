from .models import UniqueVisitor
from .utils import get_client_ip
from django.utils.deprecation import MiddlewareMixin

class UniqueVisitorMiddleware:
    """Middleware to track unique visitors by IP address"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract IP using the existing utility function
        ip_address = get_client_ip(request)
        
        if ip_address:
            # get_or_create ensures we only save unique IPs
            # We use try/except as a failsafe so database errors don't crash the site
            try:
                UniqueVisitor.objects.get_or_create(ip_address=ip_address)
            except Exception:
                pass
                
        response = self.get_response(request)
        return response

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adds headers not covered by Django's built-in security middleware
    or django-csp. Currently: Permissions-Policy.
    Do NOT set CSP, X-Frame-Options, or HSTS here — Django handles those.
    """

    def process_response(self, request, response):
        # Permissions-Policy: disable sensitive browser features
        response['Permissions-Policy'] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "interest-cohort=()"   # disables FLoC
        )
        return response
