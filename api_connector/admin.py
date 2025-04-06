from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import APIAuthentication, APIConfiguration, APIEndpoint, FunctionDefinition

class APIEndpointInline(admin.TabularInline):
    model = APIEndpoint
    extra = 1
    fields = ('name', 'path', 'http_method', 'is_active')

class FunctionDefinitionInline(admin.TabularInline):
    model = FunctionDefinition
    extra = 0
    fields = ('name', 'description', 'is_active')

@admin.register(APIAuthentication)
class APIAuthenticationAdmin(admin.ModelAdmin):
    list_display = ('name', 'auth_type', 'created_at', 'updated_at')
    list_filter = ('auth_type', 'created_at')
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'auth_type')
        }),
        (_('API Key Authentication'), {
            'fields': ('api_key', 'api_key_name'),
            'classes': ('collapse',),
        }),
        (_('Bearer Token Authentication'), {
            'fields': ('token',),
            'classes': ('collapse',),
        }),
        (_('Basic Authentication'), {
            'fields': ('username', 'password'),
            'classes': ('collapse',),
        }),
        (_('OAuth 2.0 Authentication'), {
            'fields': ('client_id', 'client_secret', 'token_url', 'refresh_token', 'access_token', 'expires_at'),
            'classes': ('collapse',),
        }),
    )

@admin.register(APIConfiguration)
class APIConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_url', 'authentication', 'is_active')
    list_filter = ('is_active', 'rate_limit_enabled', 'created_at')
    search_fields = ('name', 'base_url')
    inlines = [APIEndpointInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'base_url', 'authentication', 'is_active')
        }),
        (_('Rate Limiting'), {
            'fields': ('rate_limit_enabled', 'rate_limit'),
        }),
        (_('Retry Configuration'), {
            'fields': ('max_retries', 'retry_backoff'),
        }),
        (_('Headers'), {
            'fields': ('default_headers',),
        }),
    )

@admin.register(APIEndpoint)
class APIEndpointAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_config', 'path', 'http_method', 'is_active')
    list_filter = ('http_method', 'is_active', 'api_config')
    search_fields = ('name', 'path')
    inlines = [FunctionDefinitionInline]
    fieldsets = (
        (None, {
            'fields': ('api_config', 'name', 'description', 'path', 'http_method', 'is_active')
        }),
        (_('Request Configuration'), {
            'fields': ('request_body_template', 'request_headers'),
            'classes': ('collapse',),
        }),
        (_('Response Configuration'), {
            'fields': ('response_mapping',),
            'classes': ('collapse',),
        }),
    )

@admin.register(FunctionDefinition)
class FunctionDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_endpoint', 'is_active')
    list_filter = ('is_active', 'api_endpoint__api_config')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'api_endpoint', 'is_active')
        }),
        (_('Function Schema'), {
            'fields': ('parameters_schema',),
        }),
        (_('Parameter Mapping'), {
            'fields': ('parameter_mapping',),
        }),
    )
