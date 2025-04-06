from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import RateLimitLog, SystemConfig, ErrorLog

@admin.register(RateLimitLog)
class RateLimitLogAdmin(admin.ModelAdmin):
    list_display = ('target_type', 'target_id', 'request_count', 'limit', 'window_start', 'window_end')
    list_filter = ('target_type', 'window_start')
    search_fields = ('target_id',)
    readonly_fields = ('last_request_at',)
    fieldsets = (
        (None, {
            'fields': ('target_type', 'target_id')
        }),
        (_('Rate Limit Details'), {
            'fields': ('request_count', 'limit', 'window_start', 'window_end', 'last_request_at'),
        }),
    )
    
    def has_add_permission(self, request):
        # RateLimitLogs should be created by the system, not manually
        return False

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'updated_at')
    search_fields = ('key', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('key', 'value', 'description')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('level', 'message_short', 'component', 'created_at', 'resolved')
    list_filter = ('level', 'component', 'resolved', 'created_at')
    search_fields = ('message', 'component', 'related_object_id')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('level', 'message', 'component')
        }),
        (_('Error Details'), {
            'fields': ('traceback', 'context'),
        }),
        (_('Related Object'), {
            'fields': ('related_object_type', 'related_object_id'),
            'classes': ('collapse',),
        }),
        (_('Resolution'), {
            'fields': ('resolved', 'resolved_at', 'resolution_notes'),
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    def message_short(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_short.short_description = _('Message')
    
    def has_add_permission(self, request):
        # ErrorLogs should be created by the system, not manually
        return False
