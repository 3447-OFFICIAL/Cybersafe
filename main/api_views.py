from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    AdminUser, CyberCrime, CyberCrimeImage, ChatbotConfig, 
    ChatbotConversation, AuditLog, SecurityEvent, 
    SystemUptime, UniqueVisitor
)
from .serializers import (
    AdminUserSerializer, CyberCrimeSerializer, CyberCrimeImageSerializer, 
    ChatbotConfigSerializer, ChatbotConversationSerializer, AuditLogSerializer, 
    SecurityEventSerializer, SystemUptimeSerializer, UniqueVisitorSerializer
)

class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]

class CyberCrimeViewSet(viewsets.ModelViewSet):
    queryset = CyberCrime.objects.all()
    serializer_class = CyberCrimeSerializer
    permission_classes = [permissions.AllowAny] # Read-only for public, admin to edit
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'severity']
    search_fields = ['type', 'description']
    ordering_fields = ['created_at', 'severity']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class CyberCrimeImageViewSet(viewsets.ModelViewSet):
    queryset = CyberCrimeImage.objects.all()
    serializer_class = CyberCrimeImageSerializer
    permission_classes = [permissions.IsAdminUser]

class ChatbotConfigViewSet(viewsets.ModelViewSet):
    queryset = ChatbotConfig.objects.all()
    serializer_class = ChatbotConfigSerializer
    permission_classes = [permissions.IsAdminUser]

class ChatbotConversationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChatbotConversation.objects.all()
    serializer_class = ChatbotConversationSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['success']
    ordering_fields = ['created_at', 'response_time']

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['action', 'resource_type', 'admin_user__username']
    ordering_fields = ['timestamp']

class SecurityEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SecurityEvent.objects.all()
    serializer_class = SecurityEventSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event_type', 'severity']
    ordering_fields = ['timestamp']

class SystemUptimeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemUptime.objects.all()
    serializer_class = SystemUptimeSerializer
    permission_classes = [permissions.IsAdminUser]

class UniqueVisitorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UniqueVisitor.objects.all()
    serializer_class = UniqueVisitorSerializer
    permission_classes = [permissions.IsAdminUser]
