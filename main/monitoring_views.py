from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.utils import timezone
from django.db import connection
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SecurityEvent, SystemUptime
from .serializers import SecurityEventSerializer, SystemUptimeSerializer
import platform
import psutil
import datetime
import csv
from django.http import HttpResponse

@login_required
def export_security_logs(request):
    """Export security events to CSV"""
    if not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="security_audit_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Event Type', 'Severity', 'IP Address', 'User Agent', 'Description'])
    
    events = SecurityEvent.objects.all().order_by('-timestamp')
    for event in events:
        writer.writerow([
            event.timestamp,
            event.event_type,
            event.severity,
            event.ip_address,
            event.user_agent,
            event.description
        ])
        
    return response

@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_health_api(request):
    """API for system health status"""
    health_data = {
        'status': 'Healthy',
        'database': 'Connected',
        'server': 'Running',
        'timestamp': timezone.now(),
        'details': {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'cpu_usage': f"{psutil.cpu_percent()}%",
            'memory_usage': f"{psutil.virtual_memory().percent}%",
        }
    }
    
    # Check database connection
    try:
        connection.ensure_connection()
    except Exception as e:
        health_data['database'] = 'Error'
        health_data['status'] = 'Critical'
        health_data['error'] = str(e)
        
    return Response(health_data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_uptime_api(request):
    """API for system uptime"""
    uptime_obj = SystemUptime.objects.first()
    if not uptime_obj:
        # Create a default if none exists
        uptime_obj = SystemUptime.objects.create()
        
    serializer = SystemUptimeSerializer(uptime_obj)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def security_stats_api(request):
    """API for security monitoring stats"""
    stats = {
        'total_events': SecurityEvent.objects.count(),
        # Only count 'critical' for the Critical Issues box
        'high_severity': SecurityEvent.objects.filter(severity='critical').count(),
        'failed_logins': SecurityEvent.objects.filter(event_type='failed_login').count(),
        'rate_limits': SecurityEvent.objects.filter(event_type='rate_limit').count(),
        # Count both suspicious activity and unauthorized access as "Activity"
        'suspicious_activities': SecurityEvent.objects.filter(
            event_type__in=['suspicious_activity', 'unauthorized_access']
        ).count(),
        'invalid_tokens': SecurityEvent.objects.filter(event_type='invalid_token').count(),
        # Added severity counts for the doughnut chart
        'severity_counts': [
            SecurityEvent.objects.filter(severity='low').count(),
            SecurityEvent.objects.filter(severity='medium').count(),
            SecurityEvent.objects.filter(severity='high').count(),
            SecurityEvent.objects.filter(severity='critical').count(),
        ]
    }
    return Response(stats)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def security_events_api(request):
    """API for security event logs"""
    events = SecurityEvent.objects.all()[:50]  # Get last 50 events
    serializer = SecurityEventSerializer(events, many=True)
    return Response(serializer.data)

@login_required
def monitoring_dashboard(request):
    """View for rendering the monitoring dashboard page"""
    if not request.user.is_staff:
        # Log Unauthorized Access
        from .utils import log_security_event
        log_security_event(
            event_type='unauthorized_access',
            severity='critical',
            description=f"Unauthorized access attempt to monitoring dashboard by user: {request.user.email}",
            request=request
        )
        return redirect('home')
        
    return render(request, 'admin/monitoring_dashboard.html')
