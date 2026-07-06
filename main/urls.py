from django.urls import path, include
from . import views, monitoring_views, views_api

urlpatterns = [
    path('', views.home, name='home'),
    path('cyber-crimes/', views.cyber_crimes, name='cyber_crimes'),
    path('crime/<uuid:crime_id>/', views.crime_detail, name='crime_detail'),
    path('report/', views.report_crime, name='report_crime'),
    path('reporting-guide/', views.reporting_guide, name='reporting_guide'),
    path('risk-calculator/', views.risk_calculator, name='risk_calculator'),
    path('contact/', views.contact, name='contact'),
    path('citizen-safety/', views.citizen_safety, name='citizen_safety'),
    path('email-breach-check/', views.email_breach_check, name='email_breach_check'),
    path('phone-exposure-check/', views.phone_exposure_check, name='phone_exposure_check'),
    path('aadhaar-risk-check/', views.aadhaar_risk_check, name='aadhaar_risk_check'),
    path('financial-risk-scan/', views.financial_risk_scan, name='financial_risk_scan'),
    path('kyc-document-shield/', views.kyc_document_shield, name='kyc_document_shield'),
    path('password-strength-scan/', views.password_strength_scan, name='password_strength_scan'),
    path('darkweb/', views.dark_web, name='dark_web'),

    path('admin-access/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/crimes/', views.admin_crimes, name='admin_crimes'),
    path('admin/chatbot/', views.admin_chatbot, name='admin_chatbot'),
    path('admin/customize-bot/', views.customize_bot, name='customize_bot'),
    path('admin/logs/', views.logs_view, name='logs_view'),
    path('admin/visitors/', views.admin_visitors, name='admin_visitors'),
    path("admin/bulk-delete/", views.bulk_delete, name="bulk_delete"),
    path("admin/bulk-update-severity/", views.bulk_update_severity, name="bulk_update_severity"),

    path('admin/monitoring/', monitoring_views.monitoring_dashboard, name='monitoring_dashboard'),
    path('admin/monitoring/export/', monitoring_views.export_security_logs, name='export_security_logs'),

    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('api/chatbot/', include('chatbot.urls')),
    path('api/increment-clicks/', views.increment_clicks, name='increment_clicks'),
    path('admin/crimes/<uuid:crime_id>/data/', views.crime_data_api, name='crime_data_api'),

    # TF-IDF Search Engine APIs
    path('api/threat-intelligence/search/', views_api.SearchAPIView.as_view(), name='threat_search_api'),
    path('api/threat-intelligence/related/', views_api.RelatedThreatsAPIView.as_view(), name='threat_related_api'),

    # Monitoring APIs
    path('api/system/health/', monitoring_views.system_health_api, name='system_health_api'),
    path('api/system/uptime/', monitoring_views.system_uptime_api, name='system_uptime_api'),
    path('api/security/stats/', monitoring_views.security_stats_api, name='security_stats_api'),
    path('api/security/events/', monitoring_views.security_events_api, name='security_events_api'),

    # Scorecard & Assessment
    path('scorecard/', views.scorecard, name='scorecard'),
    path('assessment/', views.security_assessment, name='security_assessment'),
    path('download-report/<uuid:assessment_id>/', views.download_scorecard_pdf, name='download_scorecard_pdf'),
]