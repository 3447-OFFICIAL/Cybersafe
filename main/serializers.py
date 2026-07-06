from rest_framework import serializers
from .models import (
    SecurityEvent, SystemUptime, AdminUser, CyberCrime, 
    CyberCrimeImage, ChatbotConfig, ChatbotConversation, 
    AuditLog, UniqueVisitor
)

class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = ['id', 'event_type', 'severity', 'ip_address', 'description', 'timestamp']

class SystemUptimeSerializer(serializers.ModelSerializer):
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = SystemUptime
        fields = ['start_time', 'last_check', 'duration']

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'login_attempts', 'locked_until', 'last_login', 'created_at']
        read_only_fields = ['id', 'created_at', 'last_login']

class CyberCrimeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CyberCrimeImage
        fields = ['id', 'image', 'caption', 'created_at']

class CyberCrimeSerializer(serializers.ModelSerializer):
    additional_images = CyberCrimeImageSerializer(many=True, read_only=True)
    banner_image_url = serializers.CharField(source='get_banner_image_url', read_only=True)
    prevention_tips_list = serializers.ListField(source='get_prevention_tips_list', read_only=True)
    reporting_steps_list = serializers.ListField(source='get_reporting_steps_list', read_only=True)

    class Meta:
        model = CyberCrime
        fields = [
            'id', 'type', 'description', 'category', 'severity', 
            'how_it_works', 'impact', 'solution', 'banner_image', 
            'banner_image_url', 'prevention_tips', 'prevention_tips_list', 
            'reporting_steps', 'reporting_steps_list', 'learn_more_clicks', 
            'additional_images', 'created_at', 'updated_at'
        ]

class ChatbotConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotConfig
        fields = ['id', 'gemini_model', 'system_prompt', 'is_active', 'created_at', 'updated_at']

class ChatbotConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotConversation
        fields = ['id', 'user_message', 'bot_response', 'response_time', 'success', 'error_message', 'ip_address', 'user_agent', 'created_at']

class AuditLogSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source='admin_user.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'admin_user', 'admin_username', 'action', 'resource_type', 'resource_id', 'details', 'ip_address', 'user_agent', 'timestamp']

class UniqueVisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniqueVisitor
        fields = ['id', 'ip_address', 'first_visit']
