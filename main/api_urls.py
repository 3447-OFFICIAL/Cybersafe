from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    AdminUserViewSet, CyberCrimeViewSet, CyberCrimeImageViewSet,
    ChatbotConfigViewSet, ChatbotConversationViewSet, AuditLogViewSet,
    SecurityEventViewSet, SystemUptimeViewSet, UniqueVisitorViewSet
)

router = DefaultRouter()
router.register(r'admin-users', AdminUserViewSet, basename='api-adminuser')
router.register(r'cyber-crimes', CyberCrimeViewSet, basename='api-cybercrime')
router.register(r'cyber-crime-images', CyberCrimeImageViewSet, basename='api-cybercrimeimage')
router.register(r'chatbot-configs', ChatbotConfigViewSet, basename='api-chatbotconfig')
router.register(r'chatbot-conversations', ChatbotConversationViewSet, basename='api-chatbotconversation')
router.register(r'audit-logs', AuditLogViewSet, basename='api-auditlog')
router.register(r'security-events', SecurityEventViewSet, basename='api-securityevent')
router.register(r'system-uptime', SystemUptimeViewSet, basename='api-systemuptime')
router.register(r'unique-visitors', UniqueVisitorViewSet, basename='api-uniquevisitor')

urlpatterns = [
    path('', include(router.urls)),
]
