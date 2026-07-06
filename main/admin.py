from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    AdminUser, CyberCrime, CyberCrimeImage, ChatbotConfig,
    ChatbotConversation, AuditLog, SecurityEvent, SystemUptime, UniqueVisitor
)

@admin.register(AdminUser)
class AdminUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active', 'created_at')
    search_fields = ('email', 'username')
    ordering = ('email',)
    fieldsets = UserAdmin.fieldsets + (
        ('Security & Custom Info', {'fields': ('phone', 'login_attempts', 'locked_until')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Security & Custom Info', {'fields': ('phone',)}),
    )

@admin.register(CyberCrime)
class CyberCrimeAdmin(admin.ModelAdmin):
    list_display = ('type', 'category', 'severity', 'learn_more_clicks', 'created_at')
    search_fields = ('type', 'description', 'category')
    list_filter = ('severity', 'category')

@admin.register(CyberCrimeImage)
class CyberCrimeImageAdmin(admin.ModelAdmin):
    list_display = ('crime', 'caption', 'created_at')
    search_fields = ('caption',)
    list_filter = ('created_at',)

@admin.register(ChatbotConfig)
class ChatbotConfigAdmin(admin.ModelAdmin):
    list_display = ('gemini_model', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)

@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ('user_message', 'bot_response', 'response_time', 'success', 'created_at')
    search_fields = ('user_message', 'bot_response')
    list_filter = ('success', 'created_at')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('admin_user', 'action', 'resource_type', 'resource_id', 'timestamp')
    search_fields = ('action', 'resource_type', 'resource_id')
    list_filter = ('timestamp',)

@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'severity', 'ip_address', 'timestamp')
    search_fields = ('event_type', 'description', 'ip_address')
    list_filter = ('severity', 'event_type', 'timestamp')

@admin.register(SystemUptime)
class SystemUptimeAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'last_check', 'duration')

@admin.register(UniqueVisitor)
class UniqueVisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'first_visit')
    search_fields = ('ip_address',)
    list_filter = ('first_visit',)
