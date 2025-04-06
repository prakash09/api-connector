from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import PromptTemplate, FunctionCallLog, AIModelConfiguration

@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'ai_model_config', 'model', 'temperature', 'function_calling_enabled', 'is_active')
    list_filter = ('ai_model_config', 'model', 'function_calling_enabled', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'system_prompt', 'user_prompt_template')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('Prompt Content'), {
            'fields': ('system_prompt', 'user_prompt_template'),
        }),
        (_('Model Configuration'), {
            'fields': ('ai_model_config', 'model', 'temperature', 'max_tokens'),
        }),
        (_('Function Calling'), {
            'fields': ('function_calling_enabled',),
        }),
    )

@admin.register(FunctionCallLog)
class FunctionCallLogAdmin(admin.ModelAdmin):
    list_display = ('function_name', 'status', 'execution_time', 'created_at')
    list_filter = ('status', 'function_name', 'created_at')
    search_fields = ('function_name', 'function_arguments', 'error_message')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('function_name', 'message')
        }),
        (_('Function Details'), {
            'fields': ('function_arguments',),
        }),
        (_('Execution'), {
            'fields': ('status', 'result', 'error_message', 'execution_time'),
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def has_add_permission(self, request):
        # FunctionCallLogs should be created by the system, not manually
        return False


@admin.register(AIModelConfiguration)
class AIModelConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'default_model', 'is_active', 'created_at')
    list_filter = ('model_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'base_url', 'default_model')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'model_type', 'is_active')
        }),
        (_('API Configuration'), {
            'fields': ('base_url', 'api_key', 'organization_id'),
        }),
        (_('Default Parameters'), {
            'fields': ('default_model', 'default_temperature', 'default_max_tokens'),
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
