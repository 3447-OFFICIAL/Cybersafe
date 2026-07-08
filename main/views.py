from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ValidationError
import logging
import json
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import ScopedRateThrottle, AnonRateThrottle, UserRateThrottle
from rest_framework.authentication import SessionAuthentication
from chatbot.orchestrator import orchestrate, count_tokens
from chatbot.gemini_client import generate
from chatbot.session_manager import get_session_id

# Initialize logger
logger = logging.getLogger(__name__)

load_dotenv()

from .models import (
    AdminUser,
    CyberCrime,
    CyberCrimeImage,
    ChatbotConfig,
    ChatbotConversation,
    AuditLog,
    SecurityEvent,
    UniqueVisitor
)

from .forms import ChatbotConfigForm, CyberCrimeForm, validate_image_secure
from .utils import (
    log_audit_action, get_client_ip, sanitize_input,
    validate_email, validate_phone, log_security_event
)
from .utils.system_health import get_system_health_status
    
@ensure_csrf_cookie
def home(request):
    """
    Homepage view
    """

    trending_crimes = CyberCrime.objects.all()[:6]

    context = {
        'trending_crimes': trending_crimes
    }

    return render(
        request,
        'main/home.html',
        context
    )


def cyber_crimes(request):
    return CyberCrimeListView.as_view()(request)


def crime_detail(request, crime_id):
    return CyberCrimeDetailView.as_view()(request, crime_id=crime_id)


def report_crime(request):
    return ReportCrimeView.as_view()(request)


def reporting_guide(request):
    return ReportingGuideView.as_view()(request)


def risk_calculator(request):
    return RiskCalculatorView.as_view()(request)


def contact(request):
    return ContactView.as_view()(request)


def citizen_safety(request):
    return CitizenSafetyView.as_view()(request)


def email_breach_check(request):
    return EmailBreachCheckView.as_view()(request)


def phone_exposure_check(request):
    return PhoneExposureCheckView.as_view()(request)


def aadhaar_risk_check(request):
    return AadhaarRiskCheckView.as_view()(request)


def financial_risk_scan(request):
    return FinancialRiskScanView.as_view()(request)


def kyc_document_shield(request):
    return KycDocumentShieldView.as_view()(request)


def password_strength_scan(request):
    return PasswordStrengthScanView.as_view()(request)


def dark_web(request):
    return DarkWebView.as_view()(request)


def download_scorecard_pdf(request, assessment_id):
    """Generate and return the personalized CyberSafe Scorecard PDF."""
    from .models import SecurityAssessmentResult
    from main.services.pdf_service import generate_pdf
    from django.http import Http404

    # Fetch the assessment result
    try:
        result = get_object_or_404(SecurityAssessmentResult, id=assessment_id)
    except (ValidationError, ValueError, Http404):
        # Handle invalid UUID format or missing record gracefully
        return HttpResponse("Assessment record not found.", status=404, content_type="text/plain")

    # Set up HTTP response headers
    response = HttpResponse(content_type='application/pdf')
    filename = f"CyberSafe_Scorecard_{str(result.id)[:8]}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    try:
        # Get historical attempts list from user session
        history_attempts = request.session.get('assessment_history', [])
        # Pass the response buffer to the generator
        generate_pdf(result, history_attempts, response)
        return response
    except Exception as e:
        logger.error(f"Failed to generate scorecard PDF for {assessment_id}: {str(e)}", exc_info=True)
        return HttpResponse(f"Error generating report PDF: {str(e)}", status=500, content_type="text/plain")


def admin_logout(request):
    return AdminLogoutView.as_view()(request)


def admin_dashboard(request):
    return AdminDashboardView.as_view()(request)


def admin_crimes(request):
    return AdminCrimesView.as_view()(request)


@ensure_csrf_cookie
def admin_chatbot(request):
    return AdminChatbotView.as_view()(request)


def customize_bot(request):
    return CustomizeBotView.as_view()(request)

@ensure_csrf_cookie
def chatbot_api(request):
    return ChatbotAPIView.as_view()(request)


def increment_clicks(request):
    return IncrementClicksAPIView.as_view()(request)


def crime_data_api(request, crime_id):
    return CrimeDataAPIView.as_view()(request, crime_id=crime_id)


@login_required
def logs_view(request):
    """Full audit logs view with pagination"""
    if not request.user.is_staff:
        log_security_event(
            event_type='unauthorized_access',
            severity='critical',
            description=f"Unauthorized access attempt to admin audit logs by user: {request.user.email}",
            request=request
        )
        return redirect('home')
        
    logs_list = AuditLog.objects.select_related('admin_user').order_by('-timestamp')
    
    paginator = Paginator(logs_list, 15) # Show 15 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'admin/logs.html', context)


@login_required
def admin_visitors(request):
    """View to display all unique website visitors"""
    if not request.user.is_staff:
        log_security_event(
            event_type='unauthorized_access',
            severity='critical',
            description=f"Unauthorized access attempt to admin visitors by user: {request.user.email}",
            request=request
        )
        return redirect('home')
        
    visitors_list = UniqueVisitor.objects.all().order_by('-first_visit')
    paginator = Paginator(visitors_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_visitors': visitors_list.count()
    }
    return render(request, 'admin/visitors.html', context)


@login_required
@require_POST
def bulk_delete(request):
    """Bulk delete cyber crimes"""
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)
        
    try:
        data = json.loads(request.body)
        ids = data.get("ids", [])
        
        if not ids:
            return JsonResponse({"error": "No records selected"}, status=400)
            
        # Get count for audit log
        count = CyberCrime.objects.filter(id__in=ids).count()
        
        # Perform deletion
        CyberCrime.objects.filter(id__in=ids).delete()
        
        # Log audit action
        log_audit_action(
            request, request.user, 'DELETE_BULK', 'CyberCrime', 'Multiple',
            {'count': count, 'details': f"Bulk deleted {count} cyber crimes"}
        )
        
        return JsonResponse({"status": "success", "message": f"Successfully deleted {count} records"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_POST
def bulk_update_severity(request):
    """Bulk update severity for cyber crimes"""
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)
        
    try:
        data = json.loads(request.body)
        ids = data.get("ids", [])
        severity = data.get("severity")
        
        if not ids or not severity:
            return JsonResponse({"error": "Select records and severity"}, status=400)
            
        target_severity = None
        for val, _ in CyberCrime.SEVERITY_CHOICES:
            if val.lower() == severity.lower():
                target_severity = val
                break
        
        if not target_severity:
            return JsonResponse({"error": "Invalid severity level"}, status=400)
            
        # Get count for audit log
        count = CyberCrime.objects.filter(id__in=ids).count()
        
        # Perform update
        CyberCrime.objects.filter(id__in=ids).update(severity=target_severity)
        
        # Log audit action
        log_audit_action(
            request, request.user, 'UPDATE_BULK', 'CyberCrime', 'Multiple',
            {'severity': target_severity, 'count': count, 'details': f"Bulk updated severity to {target_severity} for {count} cyber crimes"}
        )
        
        return JsonResponse({"status": "success", "message": f"Successfully updated {count} records to {target_severity}"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
class AdminCrimesView(LoginRequiredMixin, View):
    """Admin crimes management"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not request.user.is_staff:
            log_security_event(
                event_type='unauthorized_access',
                severity='critical',
                description=f"Unauthorized access attempt to admin crimes by user: {request.user.email}",
                request=request
            )
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        crimes = CyberCrime.objects.all()
        # Calculate statistics
        total_crimes = crimes.count()
        critical_count = crimes.filter(severity='critical').count()
        total_views = crimes.aggregate(total=Sum('learn_more_clicks'))['total'] or 0
        
        # Calculate average severity (convert to numeric for calculation)
        severity_values = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        total_severity = sum(severity_values.get(crime.severity.lower(), 1) for crime in crimes)
        avg_severity = round(total_severity / total_crimes, 1) if total_crimes > 0 else 0
        
        context = {
            'crimes': crimes,
            'categories': CyberCrime.CATEGORY_CHOICES,
            'severity_choices': CyberCrime.SEVERITY_CHOICES,
            'total_crimes': total_crimes,
            'critical_count': critical_count,
            'total_views': total_views,
            'avg_severity': avg_severity,
            'default_tips': json.dumps(CyberCrime.get_default_prevention_tips()),
            'default_steps': json.dumps(CyberCrime.get_default_reporting_steps()),
        }
        return render(request, 'admin/crimes.html', context)

    def post(self, request):
        # Handle delete operation first
        if 'delete_id' in request.POST:
            delete_id = request.POST.get('delete_id')
            try:
                crime = get_object_or_404(CyberCrime, id=delete_id)
                crime_type = crime.type  # Store before deletion for audit
                crime.delete()
                
                log_audit_action(
                    request, request.user, 'DELETE', 'cybercrime_data', delete_id,
                    {'type': crime_type}
                )
                
                messages.success(request, 'Crime deleted successfully.')
                return redirect('admin_crimes')
            except Exception as e:
                messages.error(request, f'Error deleting crime: {str(e)}')
                return redirect('admin_crimes')
        
        crime_id = request.POST.get('crime_id')
        if crime_id:
            try:
                crime = CyberCrime.objects.get(id=crime_id)
                form = CyberCrimeForm(request.POST, request.FILES, instance=crime)
            except CyberCrime.DoesNotExist:
                logger.error(f"Crime with ID {crime_id} not found for update")
                messages.error(request, 'Crime not found!')
                return redirect('admin_crimes')
        else:
            form = CyberCrimeForm(request.POST, request.FILES)

        if form.is_valid():
            crime = form.save()
            
            # Handle additional images
            additional_images_upload = form.cleaned_data.get('additional_images_upload') or []
            for img in additional_images_upload:
                CyberCrimeImage.objects.create(crime=crime, image=img)
            
            # Log audit action
            action = 'UPDATE' if crime_id else 'CREATE'
            log_audit_action(
                request, request.user, action, 'cybercrime_data', crime.id,
                {'type': crime.type}
            )
            
            logger.info(f"Crime {'updated' if crime_id else 'created'} with ID: {crime.id}")
            messages.success(request, f"Crime {'updated' if crime_id else 'added'} successfully!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            logger.warning(f"CyberCrimeForm validation failed: {form.errors}")
            
        return redirect('admin_crimes')


class CrimeDataAPIView(LoginRequiredMixin, View):
    """API endpoint to get crime data for view/edit"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, crime_id):
        try:
            crime = get_object_or_404(CyberCrime, id=crime_id)
            
            # Get lists from methods
            prevention_tips = crime.get_prevention_tips_list()
            reporting_steps = crime.get_reporting_steps_list()
            images = crime.get_images_list()
            
            data = {
                'id': str(crime.id),
                'type': crime.type,
                'description': crime.description,
                'category': crime.category,
                'severity': crime.severity,
                
                # Detailed Info
                'how_it_works': crime.how_it_works,
                'impact': crime.impact,
                'solution': crime.solution,
                
                'prevention_tips': prevention_tips,
                'reporting_steps': reporting_steps,
                'banner_image': crime.banner_image.url if crime.banner_image else None,
                'images': images,
                'learn_more_clicks': crime.learn_more_clicks,
                'created_at': crime.created_at.isoformat(),
            }
            
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class HomeView(TemplateView):
    """Home page view"""
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_crimes'] = CyberCrime.objects.count()
        context['trending_crimes'] = CyberCrime.objects.order_by('-learn_more_clicks')[:4]
        return context


class CyberCrimeListView(ListView):
    """Cyber crimes listing page"""
    model = CyberCrime
    template_name = 'main/cyber_crimes.html'
    context_object_name = 'page_obj'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        category_filter = self.request.GET.get('category', '')
        
        if search_query:
            matching_categories = [
                k for k, v in CyberCrime.CATEGORY_CHOICES
                if search_query.lower() in v.lower()
            ]
            
            query = Q(type__icontains=search_query) | Q(description__icontains=search_query)
            if matching_categories:
                query |= Q(category__in=matching_categories)
            
            queryset = queryset.filter(query)
        
        if category_filter:
            queryset = queryset.filter(category=category_filter)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate real-time statistics
        total_crimes = CyberCrime.objects.count()
        critical_count = CyberCrime.objects.filter(severity='critical').count()
        high_count = CyberCrime.objects.filter(severity='high').count()
        
        context['stats'] = {
            'total': total_crimes,
            'active': critical_count + high_count,
            'critical': critical_count,
            'resolved': int(total_crimes * 0.94)
        }
        
        context['categories'] = CyberCrime.CATEGORY_CHOICES
        context['search_query'] = self.request.GET.get('search', '')
        context['category_filter'] = self.request.GET.get('category', '')
        return context



class CyberCrimeDetailView(DetailView):
    """Individual crime detail page"""
    model = CyberCrime
    template_name = 'main/crime_detail.html'
    context_object_name = 'crime'
    pk_url_kwarg = 'crime_id'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.learn_more_clicks += 1
        obj.save()
        return obj



class ReportCrimeView(View):
    """Report crime page (Need Help?)"""
    def get(self, request):
        return render(request, 'main/report_crime.html')
        
    def post(self, request):
        messages.success(request, 'Your report has been submitted successfully.')
        return redirect('report_crime')


class ReportingGuideView(TemplateView):
    template_name = 'main/reporting_guide.html'


class RiskCalculatorView(TemplateView):
    template_name = 'main/risk_calculator.html'


class ContactView(TemplateView):
    template_name = 'main/contact.html'


class CitizenSafetyView(TemplateView):
    template_name = 'main/citizen_safety.html'


class EmailBreachCheckView(TemplateView):
    template_name = 'main/email_breach.html'


class PhoneExposureCheckView(TemplateView):
    template_name = 'main/phone_exposure.html'


class AadhaarRiskCheckView(TemplateView):
    template_name = 'main/aadhaar_risk.html'


class FinancialRiskScanView(TemplateView):
    template_name = 'main/financial_risk.html'


class KycDocumentShieldView(TemplateView):
    template_name = 'main/kyc_shield.html'


class PasswordStrengthScanView(TemplateView):
    template_name = 'main/password_scan.html'


class DarkWebView(TemplateView):
    template_name = 'main/darkweb.html'


def admin_login(request):
    """Admin login page"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        logger.info(f"LOGIN ATTEMPT RECEIVED FOR {email}")
        
        # Check email format using validate_email
        if not validate_email(email):
            logger.warning(f"Login attempt failed due to invalid email format: {email}")
            messages.error(request, 'Invalid email format.')
            return render(request, 'admin/login.html')
        
        try:
            user = AdminUser.objects.filter(email__iexact=email).first()
            if not user:
                logger.warning(f"Login failed: User not found for {email}")
                
                # Log to Security Monitoring Dashboard
                log_security_event(
                    event_type='failed_login',
                    severity='medium',
                    description=f"Login attempt for non-existent user: {email}",
                    request=request
                )
                
                messages.error(request, 'Invalid credentials.')
                return render(request, 'admin/login.html')
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"Login failed: User {email} is inactive")
                messages.error(request, 'Invalid credentials.')
                return render(request, 'admin/login.html')
            
            # Check if account is locked
            if user.locked_until and user.locked_until > timezone.now():
                logger.warning(f"Login failed: Account locked for {email}")
                messages.error(request, 'Account is temporarily locked. Please try again later.')
                return render(request, 'admin/login.html')
            
            # Authenticate using Django auth backend
            authenticated_user = authenticate(request, username=email, password=password)
            
            # Fallback for custom user model authentication quirks
            if not authenticated_user and user.check_password(password):
                if not user.is_active:
                    logger.warning(f"Login failed: User {email} is inactive (fallback)")
                    messages.error(request, 'Invalid credentials.')
                    return render(request, 'admin/login.html')
                logger.info(f"authenticate() failed but check_password() passed for {email}. Manually logging in.")
                authenticated_user = user
                # Ensure backend is set for session persistence
                authenticated_user.backend = 'django.contrib.auth.backends.ModelBackend'
            
            if authenticated_user:
                # Verify that the user is a staff member
                if not authenticated_user.is_staff:
                    logger.warning(f"Login failed: User {email} is not a staff member")
                    messages.error(request, 'Invalid credentials.')
                    return render(request, 'admin/login.html')
                
                # Reset login attempts
                user.login_attempts = 0
                user.locked_until = None
                user.last_login = timezone.now()
                user.save()
                
                login(request, authenticated_user)
                logger.info(f"Successfully logged in {email}")
                
                # Log audit action
                log_audit_action(
                    request, authenticated_user, 'LOGIN_SUCCESS', 'admin_users', authenticated_user.id,
                    {'ip_address': get_client_ip(request)}
                )
                
                return redirect('admin_dashboard')
            else:
                # Increment failed login attempts
                user.login_attempts += 1
                logger.warning(f"Login failed: Password incorrect for {email} (Attempt {user.login_attempts})")
                if user.login_attempts >= 5:
                    user.locked_until = timezone.now() + timedelta(minutes=30)
                user.save()
                
                # Log failed attempt
                AuditLog.objects.create(
                    admin_user=user,
                    action='LOGIN_FAILURE',
                    resource_type='admin_users',
                    resource_id=str(user.id),
                    details={'ip_address': get_client_ip(request), 'attempted_email': email},
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', 'Unknown')
                )
                
                # Log to Security Monitoring Dashboard
                log_security_event(
                    event_type='failed_login',
                    severity='medium',
                    description=f"Failed login attempt for email: {email}",
                    request=request
                )
                
                messages.error(request, 'Invalid credentials.')
                
        except Exception as e:
            logger.exception(f"Exception during login for {email}")
            messages.error(request, f'An internal error occurred: {str(e)}')
    
    return render(request, 'admin/login.html')


class AdminLogoutView(LoginRequiredMixin, View):
    """Admin logout"""
    def get(self, request):
        log_audit_action(
            request, request.user, 'LOGOUT', 'admin_users', request.user.id,
            {'ip_address': get_client_ip(request)}
        )
        logout(request)
        return redirect('admin_login')


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    """Admin dashboard"""
    template_name = 'admin/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not request.user.is_staff:
            log_security_event(
                event_type='unauthorized_access',
                severity='critical',
                description=f"Unauthorized access attempt to admin dashboard by user: {request.user.email}",
                request=request
            )
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        total_crimes = CyberCrime.objects.count()
        trending_crimes = CyberCrime.objects.order_by('-learn_more_clicks')[:5]
        recent_activity = AuditLog.objects.select_related('admin_user').order_by('-timestamp')[:3]
        
        # Chart Data Preparation
        # 1. Crimes Over Time (Line Chart)
        crimes_over_time = (
            CyberCrime.objects
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        
        # 2. Crimes by Severity (Pie Chart)
        severity_data = (
            CyberCrime.objects
            .values('severity')
            .annotate(count=Count('id'))
        )
        
        # 3. Format Data for Template
        chart_data = {
            "dates": [str(item["date"]) for item in crimes_over_time if item["date"]],
            "counts": [item["count"] for item in crimes_over_time if item["date"]],
            "severity_labels": [item["severity"] for item in severity_data],
            "severity_counts": [item["count"] for item in severity_data],
        }
        
        # Get system health
        health_status = get_system_health_status()
        
        # Get security stats for dashboard
        critical_alerts = SecurityEvent.objects.filter(severity='critical').count()
        
        # Get unique visitors count
        unique_visitors_count = UniqueVisitor.objects.count()
        
        context.update({
            'total_crimes': total_crimes,
            'trending_crimes': trending_crimes,
            'recent_activity': recent_activity,
            'health_status': health_status,
            'critical_alerts': critical_alerts,
            'unique_visitors_count': unique_visitors_count,
            'chart_data': json.dumps(chart_data),
        })
        return context


class AdminChatbotView(LoginRequiredMixin, TemplateView):
    """Admin chatbot management - test interface only"""
    template_name = 'admin/chatbot.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = ChatbotConfig.objects.first()
        if not config:
            config = ChatbotConfig.objects.create()

        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_conversations = ChatbotConversation.objects.filter(
            created_at__gte=current_month_start
        ).count()

        recent_conversations = ChatbotConversation.objects.filter(
            success=True
        ).order_by('-created_at')[:100]

        if recent_conversations:
            avg_response_time = sum(conv.response_time for conv in recent_conversations) / len(recent_conversations)
            avg_response_time = round(avg_response_time, 1)
        else:
            avg_response_time = 0.0

        total_recent = ChatbotConversation.objects.order_by('-created_at')[:100].count()
        successful_recent = ChatbotConversation.objects.filter(
            success=True
        ).order_by('-created_at')[:100].count()

        if total_recent > 0:
            satisfaction_rate = round((successful_recent / total_recent) * 100)
        else:
            satisfaction_rate = 100

        context['config'] = config
        context['total_conversations'] = monthly_conversations
        context['avg_response_time'] = avg_response_time
        context['satisfaction_rate'] = satisfaction_rate
        return context


class ChatbotAPIView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "chatbot"

    def post(self, request):

        import time

        start_time = time.time()

        try:

            message = request.data.get("message", "").strip()

            if not message:
                return JsonResponse({
                    "response": "Please enter a message."
                }, status=400)

            session_id = get_session_id(request)

            reply, mode, category = orchestrate(
                request,
                message,
                generate
            )

            response_time = time.time() - start_time

            # Token counting
            input_tokens = count_tokens(message)
            output_tokens = count_tokens(reply)
            total_tokens = input_tokens + output_tokens

            # Conversation logging
            ChatbotConversation.objects.create(
                user_message=message,
                bot_response=reply,
                response_time=response_time,
                success=True,
                ip_address=get_client_ip(request),
                user_agent=request.META.get(
                    "HTTP_USER_AGENT",
                    ""
                )
            )

            return JsonResponse({
                "response": reply,
                "mode": mode,
                "category": category,
                "session_id": session_id,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens
                }
            })

        except Exception as e:

            logger.error(
                f"Chatbot API Error: {str(e)}",
                exc_info=True
            )

            response_time = time.time() - start_time

            ChatbotConversation.objects.create(
                user_message=message if "message" in locals() else "Unknown",
                bot_response=f"Error: {str(e)}",
                response_time=response_time,
                success=False,
                error_message=str(e),
                ip_address=get_client_ip(request),
                user_agent=request.META.get(
                    "HTTP_USER_AGENT",
                    ""
                )
            )

            return JsonResponse({
                "response": "Internal chatbot error."
            }, status=500)
        
class CustomizeBotView(LoginRequiredMixin, View):
    """Customize bot configuration page"""

    def get(self, request):
        config = ChatbotConfig.objects.first()

        if not config:
            config = ChatbotConfig.objects.create()

        form = ChatbotConfigForm(instance=config)

        return render(
            request,
            'admin/customize_bot.html',
            {'form': form, 'config': config}
        )

    def post(self, request):
        config = ChatbotConfig.objects.first()

        if not config:
            config = ChatbotConfig.objects.create()

        form = ChatbotConfigForm(request.POST, instance=config)

        if form.is_valid():
            saved_config = form.save(commit=False)
            if not form.cleaned_data.get('gemini_api_key'):
                saved_config.gemini_api_key = config.gemini_api_key
            saved_config.save()
            messages.success(request, 'Bot configuration updated successfully!')
            return redirect('customize_bot')

        return render(
            request,
            'admin/customize_bot.html',
            {'form': form, 'config': config}
        )


class IncrementClicksAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        crime_id = request.data.get('crime_id')
        if not crime_id:
            return JsonResponse({'error': 'crime_id is required'}, status=400)
        try:
            crime = CyberCrime.objects.get(id=crime_id)
            crime.learn_more_clicks += 1
            crime.save()
            return JsonResponse({'status': 'success', 'clicks': crime.learn_more_clicks})
        except CyberCrime.DoesNotExist:
            return JsonResponse({'error': 'CyberCrime not found'}, status=404)


from main.services.search_service import search_engine


class SearchAPIView(APIView):
    """TF-IDF powered intelligent search endpoint"""
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.GET.get('q', '')

        if not query:
            crimes = CyberCrime.objects.all().order_by('-created_at')
            serializer = CyberCrimeSerializer(crimes, many=True)
            return Response({'results': serializer.data, 'related_domains': []})

        # Get TF-IDF ranked results
        search_results = search_engine.search(query)

        response_data = []
        related_domains = set()

        for result in search_results:
            try:
                crime = CyberCrime.objects.get(id=result['id'])

                if crime.related_domains:
                    related_domains.update(crime.related_domains)

                crime_data = CyberCrimeSerializer(crime).data
                crime_data['relevance_score'] = result['score']
                response_data.append(crime_data)

            except CyberCrime.DoesNotExist:
                pass

        return Response({
            'results': response_data,
            'related_domains': list(related_domains)[:5]
        })

def security_assessment(request):
    """Handle assessment display, randomization, and submission processing."""
    import json
    import random
    from .models import SecurityQuestion, SecurityAssessmentResult

    # In-memory fallback questions for production safety if the database query fails or is empty
    fallback_pool = {
        9001: {
            "category": "password_security",
            "category_display": "Password Security",
            "text": "What is the primary benefit of using a password manager?",
            "option_a": "It prevents you from forgetting your usernames",
            "option_b": "It encrypts and stores complex, unique passwords for every site",
            "option_c": "It automatically changes your passwords every day",
            "option_d": "It stops hackers from guessing your network IP",
            "correct_option": "B",
            "explanation": "Password managers generate, encrypt, and securely store unique passwords for every service, reducing the risk of credential stuffing."
        },
        9002: {
            "category": "phishing",
            "category_display": "Phishing & Scams",
            "text": "You receive an urgent email from 'support@paypa1.com' asking you to verify your account. What should you do?",
            "option_a": "Click the link and verify",
            "option_b": "Reply and ask if it's real",
            "option_c": "Ignore it or navigate directly to the official site by typing the URL yourself",
            "option_d": "Forward it to all your friends to warn them",
            "correct_option": "C",
            "explanation": "The domain is misspelled ('paypa1'). Always ignore suspicious links and go directly to the known official website."
        },
        9003: {
            "category": "banking_fraud",
            "category_display": "Banking Fraud",
            "text": "Your bank calls you asking for the OTP you just received to 'block a fraudulent transaction'. What do you do?",
            "option_a": "Provide the OTP immediately to stop the fraud",
            "option_b": "Hang up; banks never ask for OTPs over the phone",
            "option_c": "Ask them to verify your account balance first",
            "option_d": "Forward the SMS to the caller",
            "correct_option": "B",
            "explanation": "Legitimate banks will never ask you to read out an OTP. The caller is the fraudster trying to authorize a transaction."
        },
        9004: {
            "category": "upi_scams",
            "category_display": "UPI Scams",
            "text": "A buyer on an online marketplace says they sent a 'Request Money' link for you to receive payment. What should you do?",
            "option_a": "Enter your UPI PIN to accept the money",
            "option_b": "Decline it; you never enter a UPI PIN to receive money, only to send it",
            "option_c": "Share your bank account details instead",
            "option_d": "Call customer support to verify the link",
            "correct_option": "B",
            "explanation": "Entering a UPI PIN authorizes a deduction from your account. You NEVER need a PIN to receive funds."
        },
        9005: {
            "category": "public_wifi",
            "category_display": "Public WiFi",
            "text": "What is the biggest risk of using unsecured Public WiFi?",
            "option_a": "Slower internet speeds",
            "option_b": "Data interception by attackers on the same network (Man-in-the-Middle attacks)",
            "option_c": "Getting banned from the cafe",
            "option_d": "Using too much bandwidth",
            "correct_option": "B",
            "explanation": "Unsecured WiFi transmits data in cleartext, allowing attackers to intercept passwords and cookies."
        }
    }

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            answers = data.get('answers', {})
            quiz_mapping = request.session.get('quiz_mapping', {})
            
            score = 0
            total = len(answers)
            category_stats = {}
            weaknesses = []
            strengths = []
            
            for q_id_str, user_letter in answers.items():
                q_id = int(q_id_str)
                try:
                    q = SecurityQuestion.objects.get(id=q_id)
                    category = q.category
                    category_display = q.get_category_display()
                    correct_option = q.correct_option
                except SecurityQuestion.DoesNotExist:
                    if q_id in fallback_pool:
                        fq = fallback_pool[q_id]
                        category = fq["category"]
                        category_display = fq["category_display"]
                        correct_option = fq["correct_option"]
                    else:
                        continue

                if category not in category_stats:
                    category_stats[category] = {'total': 0, 'correct': 0, 'percentage': 0, 'name': category_display}
                
                category_stats[category]['total'] += 1
                
                mapping = quiz_mapping.get(q_id_str)
                if mapping:
                    original_letter = mapping.get(user_letter)
                    if original_letter == correct_option:
                        score += 10
                        category_stats[category]['correct'] += 1
                else:
                    if user_letter == correct_option:
                        score += 10
                        category_stats[category]['correct'] += 1
            
            total_possible = total * 10
            percentage = round((score / total_possible) * 100) if total_possible > 0 else 0
                
            if percentage >= 90:
                risk_level = 'Cyber Champion'
            elif percentage >= 75:
                risk_level = 'Security Aware'
            elif percentage >= 60:
                risk_level = 'Moderate Risk'
            elif percentage >= 40:
                risk_level = 'High Risk'
            else:
                risk_level = 'Critical Risk'
                
            for cat, stats in category_stats.items():
                pct = round((stats['correct'] / stats['total']) * 100) if stats['total'] > 0 else 0
                stats['percentage'] = pct
                if pct < 60:
                    if stats['name'] not in weaknesses:
                        weaknesses.append(stats['name'])
                elif pct >= 80:
                    if stats['name'] not in strengths:
                        strengths.append(stats['name'])
                        
            result = SecurityAssessmentResult.objects.create(
                score=score,
                total=total_possible,
                risk_level=risk_level,
                category_scores=category_stats,
                weaknesses=weaknesses,
                strengths=strengths
            )
            
            # Store in session for scorecard history
            history = request.session.get('assessment_history', [])
            history.append(str(result.id))
            request.session['assessment_history'] = history
            
            return JsonResponse({
                'success': True,
                'assessment_id': str(result.id),
                'score': score,
                'total': total_possible,
                'percentage': percentage,
                'risk_level': risk_level,
                'category_scores': category_stats,
                'weaknesses': weaknesses,
                'strengths': strengths
            })
        except Exception as e:
            logger.error(f"Error processing security assessment: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)})

    # GET Request: Generate Quiz
    try:
        all_questions = list(SecurityQuestion.objects.filter(is_active=True))
    except Exception as db_err:
        logger.error(f"Database health check failed during assessment query: {db_err}")
        all_questions = []

    questions_data = []
    quiz_mapping = {}

    if not all_questions:
        # DB is empty or down: trigger fail-safe fallback questions
        logger.warning("No security questions found in the database. Using fallback local questions.")
        for q_id, q in fallback_pool.items():
            options = [
                ('A', q['option_a']),
                ('B', q['option_b']),
                ('C', q['option_c']),
                ('D', q['option_d'])
            ]
            random.shuffle(options)
            
            new_options = {}
            new_correct_letter = 'A'
            q_mapping = {}
            
            for i, letter in enumerate(['A', 'B', 'C', 'D']):
                original_letter = options[i][0]
                new_options[f'option_{letter.lower()}'] = options[i][1]
                q_mapping[letter] = original_letter
                if original_letter == q['correct_option']:
                    new_correct_letter = letter
                    
            quiz_mapping[str(q_id)] = q_mapping
            
            questions_data.append({
                'id': q_id,
                'text': q['text'],
                'get_category_display': q['category_display'],
                'category': q['category'],
                'option_a': new_options['option_a'],
                'option_b': new_options['option_b'],
                'option_c': new_options['option_c'],
                'option_d': new_options['option_d'],
                'correct_option': new_correct_letter,
                'explanation': q['explanation']
            })
        request.session['quiz_mapping'] = quiz_mapping
        return render(request, 'main/assessment_quiz.html', {'questions': questions_data})

    random.shuffle(all_questions)
    selected_questions = all_questions[:15]
    
    for q in selected_questions:
        options = [
            ('A', q.option_a),
            ('B', q.option_b),
            ('C', q.option_c),
            ('D', q.option_d)
        ]
        random.shuffle(options)
        
        new_options = {}
        new_correct_letter = 'A'
        q_mapping = {}
        
        for i, letter in enumerate(['A', 'B', 'C', 'D']):
            original_letter = options[i][0]
            new_options[f'option_{letter.lower()}'] = options[i][1]
            q_mapping[letter] = original_letter
            if original_letter == q.correct_option:
                new_correct_letter = letter
                
        quiz_mapping[str(q.id)] = q_mapping
        
        questions_data.append({
            'id': q.id,
            'text': q.text,
            'get_category_display': q.get_category_display(),
            'category': q.category,
            'option_a': new_options['option_a'],
            'option_b': new_options['option_b'],
            'option_c': new_options['option_c'],
            'option_d': new_options['option_d'],
            'correct_option': new_correct_letter,
            'explanation': q.explanation
        })
        
    request.session['quiz_mapping'] = quiz_mapping
    return render(request, 'main/assessment_quiz.html', {'questions': questions_data})

def scorecard(request):
    """Render the persistent Cyber Safety Dashboard using assessment history."""
    import datetime
    from .models import SecurityAssessmentResult
    current_month = datetime.datetime.now().strftime("%B %Y")
    
    history_ids = request.session.get('assessment_history', [])
    assessments = SecurityAssessmentResult.objects.filter(id__in=history_ids).order_by('created_at')
    
    latest_assessment = assessments.last() if assessments.exists() else None
    
    historical_scores = []
    for a in assessments:
        pct = round((a.score / a.total) * 100) if a.total > 0 else 0
        historical_scores.append(pct)
        
    dash_offset = 283
    percentage = 0
    weak_category = None
    action_plan = "Complete a security assessment to get your personalized action plan."
    recommendations = []
    
    # Pre-define all badges for the system
    badge_definitions = {
        "Password Security": {"name": "Password Guardian", "icon": "fa-key"},
        "Phishing & Scams": {"name": "Phishing Defender", "icon": "fa-fish"},
        "Social Engineering": {"name": "Social Shield", "icon": "fa-users"},
        "Banking Fraud": {"name": "Banking Protector", "icon": "fa-university"},
        "Privacy Protection": {"name": "Privacy Keeper", "icon": "fa-lock"},
        "Mobile Security": {"name": "Mobile Defender", "icon": "fa-mobile-alt"},
        "Safe Browsing": {"name": "Safe Browser", "icon": "fa-globe"},
        "UPI Scams": {"name": "UPI Guardian", "icon": "fa-credit-card"},
        "Public WiFi": {"name": "WiFi Sentinel", "icon": "fa-wifi"},
        "Device Security": {"name": "Device Sentinel", "icon": "fa-laptop-code"}
    }
    
    badges = []
    
    if latest_assessment:
        percentage = round((latest_assessment.score / latest_assessment.total) * 100) if latest_assessment.total > 0 else 0
        dash_offset = 283 - (283 * percentage) / 100
        
        if latest_assessment.weaknesses:
            weak_category = latest_assessment.weaknesses[0]
            action_plan = f"Your score in {weak_category} is critical. Review recent guides and enable MFA."
            for w in latest_assessment.weaknesses:
                recommendations.append(f"Strengthen your {w} practices. Review recent case studies and enable multi-factor authentication where applicable.")
                
        # Evaluate Category Badges
        cat_scores = latest_assessment.category_scores if latest_assessment.category_scores else {}
        for cat_key, b_def in badge_definitions.items():
            b_info = {
                "name": b_def["name"],
                "icon": b_def["icon"],
                "earned": False,
                "rarity": "Locked",
                "rarity_class": "badge-locked",
                "tooltip": f"Score 60% or higher in {cat_key} to unlock."
            }
            
            # Find matching category stats
            stat = None
            for key, val in cat_scores.items():
                if val.get('name') == cat_key:
                    stat = val
                    break
                    
            if stat:
                pct = stat.get('percentage', 0)
                if pct == 100:
                    b_info.update({"earned": True, "rarity": "Platinum", "rarity_class": "badge-platinum", "tooltip": f"Perfect 100% in {cat_key}!"})
                elif pct >= 90:
                    b_info.update({"earned": True, "rarity": "Gold", "rarity_class": "badge-gold", "tooltip": f"Excellent {pct}% in {cat_key}."})
                elif pct >= 80:
                    b_info.update({"earned": True, "rarity": "Silver", "rarity_class": "badge-silver", "tooltip": f"Great {pct}% in {cat_key}."})
                elif pct >= 60:
                    b_info.update({"earned": True, "rarity": "Bronze", "rarity_class": "badge-bronze", "tooltip": f"Passed {pct}% in {cat_key}."})
            
            badges.append(b_info)
            
        # Cyber Champion Badge
        champ = {
            "name": "Cyber Champion",
            "icon": "fa-trophy",
            "earned": False,
            "rarity": "Locked",
            "rarity_class": "badge-locked",
            "tooltip": "Score 90% or higher overall to unlock."
        }
        if percentage >= 90:
            champ.update({
                "earned": True,
                "rarity": "Champion",
                "rarity_class": "badge-champion",
                "tooltip": f"Achieved a master overall score of {percentage}%!"
            })
        badges.insert(0, champ)
    else:
        # User has no history; display locked badges
        champ = {"name": "Cyber Champion", "icon": "fa-trophy", "earned": False, "rarity": "Locked", "rarity_class": "badge-locked", "tooltip": "Score 90% or higher overall to unlock."}
        badges.append(champ)
        for cat_key, b_def in badge_definitions.items():
            badges.append({
                "name": b_def["name"],
                "icon": b_def["icon"],
                "earned": False,
                "rarity": "Locked",
                "rarity_class": "badge-locked",
                "tooltip": f"Score 60% or higher in {cat_key} to unlock."
            })

    vulnerability_factor = 100 - percentage

    return render(request, 'main/scorecard.html', {
        'current_month': current_month,
        'latest_assessment': latest_assessment,
        'percentage': percentage,
        'dash_offset': dash_offset,
        'vulnerability_factor': vulnerability_factor,
        'historical_scores': historical_scores,
        'weak_category': weak_category,
        'action_plan': action_plan,
        'recommendations': recommendations,
        'badges': badges
    })
