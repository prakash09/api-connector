from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class APIAuthentication(models.Model):
    """
    Model to store authentication details for APIs
    """
    AUTH_TYPE_CHOICES = [
        ('none', _('No Authentication')),
        ('api_key', _('API Key')),
        ('bearer', _('Bearer Token')),
        ('basic', _('Basic Auth')),
        ('oauth2', _('OAuth 2.0')),
    ]
    
    name = models.CharField(_('Name'), max_length=100)
    auth_type = models.CharField(_('Authentication Type'), max_length=20, choices=AUTH_TYPE_CHOICES)
    
    # API Key fields
    api_key = models.CharField(_('API Key'), max_length=255, blank=True, null=True)
    api_key_name = models.CharField(_('API Key Name'), max_length=100, blank=True, null=True, 
                                   help_text=_('Header name for the API key (e.g., X-API-Key)'))
    
    # Bearer Token fields
    token = models.CharField(_('Token'), max_length=255, blank=True, null=True)
    
    # Basic Auth fields
    username = models.CharField(_('Username'), max_length=100, blank=True, null=True)
    password = models.CharField(_('Password'), max_length=100, blank=True, null=True)
    
    # OAuth 2.0 fields
    client_id = models.CharField(_('Client ID'), max_length=255, blank=True, null=True)
    client_secret = models.CharField(_('Client Secret'), max_length=255, blank=True, null=True)
    token_url = models.URLField(_('Token URL'), blank=True, null=True)
    refresh_token = models.CharField(_('Refresh Token'), max_length=255, blank=True, null=True)
    access_token = models.CharField(_('Access Token'), max_length=255, blank=True, null=True)
    expires_at = models.DateTimeField(_('Expires At'), blank=True, null=True)
    
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('API Authentication')
        verbose_name_plural = _('API Authentications')
    
    def __str__(self):
        return f"{self.name} ({self.get_auth_type_display()})"


class APIConfiguration(models.Model):
    """
    Model to store API configurations
    """
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    base_url = models.URLField(_('Base URL'))
    authentication = models.ForeignKey(
        APIAuthentication, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='api_configurations'
    )
    
    # Rate limiting
    rate_limit_enabled = models.BooleanField(_('Rate Limit Enabled'), default=True)
    rate_limit = models.CharField(
        _('Rate Limit'), 
        max_length=50, 
        default='100/hour',
        validators=[
            RegexValidator(
                regex=r'^\d+/(?:second|minute|hour|day)$',
                message=_('Rate limit must be in format: number/timeunit (e.g., 100/hour)')
            )
        ]
    )
    
    # Retry configuration
    max_retries = models.PositiveSmallIntegerField(_('Max Retries'), default=3)
    retry_backoff = models.BooleanField(_('Retry Backoff'), default=True, 
                                       help_text=_('Use exponential backoff for retries'))
    
    # Headers
    default_headers = models.JSONField(_('Default Headers'), default=dict, blank=True)
    
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('API Configuration')
        verbose_name_plural = _('API Configurations')
    
    def __str__(self):
        return self.name


class APIEndpoint(models.Model):
    """
    Model to store API endpoints
    """
    HTTP_METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]
    
    api_config = models.ForeignKey(
        APIConfiguration, 
        on_delete=models.CASCADE,
        related_name='endpoints'
    )
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    path = models.CharField(_('Path'), max_length=255, 
                           help_text=_('Relative path from the base URL (e.g., /api/v1/users)'))
    http_method = models.CharField(_('HTTP Method'), max_length=10, choices=HTTP_METHOD_CHOICES, default='GET')
    
    # Request configuration
    request_body_template = models.JSONField(_('Request Body Template'), default=dict, blank=True,
                                           help_text=_('JSON template for the request body'))
    request_headers = models.JSONField(_('Request Headers'), default=dict, blank=True)
    
    # Response configuration
    response_mapping = models.JSONField(_('Response Mapping'), default=dict, blank=True,
                                      help_text=_('Mapping of response fields to internal fields'))
    
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('API Endpoint')
        verbose_name_plural = _('API Endpoints')
        unique_together = ('api_config', 'name')
    
    def __str__(self):
        return f"{self.api_config.name} - {self.name} ({self.http_method})"


class FunctionDefinition(models.Model):
    """
    Model to store function definitions for OpenAI function calling
    """
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'))
    parameters_schema = models.JSONField(_('Parameters Schema'), 
                                       help_text=_('JSON Schema for function parameters'))
    
    # Link to API endpoint
    api_endpoint = models.ForeignKey(
        APIEndpoint, 
        on_delete=models.CASCADE,
        related_name='function_definitions'
    )
    
    # Parameter mapping
    parameter_mapping = models.JSONField(_('Parameter Mapping'), default=dict,
                                       help_text=_('Mapping of function parameters to API request parameters'))
    
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Function Definition')
        verbose_name_plural = _('Function Definitions')
    
    def __str__(self):
        return self.name
